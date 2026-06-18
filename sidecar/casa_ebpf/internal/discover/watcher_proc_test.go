package discover

import (
	"context"
	"maps"
	"slices"
	"sync"
	"testing"
	"time"

	"github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process"
	processmocks "github.com/outshift-open/CASA/sidecar/casa_ebpf/internal/process/mocks"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

const (
	testTimeout = 2 * time.Second
)

var testProcDefaultStartedTime = time.UnixMilli(time.Now().Add(-6*time.Second).Unix() * 1000) // making sure the millisecs will always be 000

func TestProcessWatcher_Poll(t *testing.T) {
	t.Parallel()
	testCases := map[string]*struct {
		procs          map[process.PID]ProcessAttrs
		inputPIDs      map[process.PID]time.Time
		expectedEvents []*WatchEvent[ProcessAttrs]
	}{
		"Should send process created events": {
			procs: map[process.PID]ProcessAttrs{},
			inputPIDs: map[process.PID]time.Time{
				process.PID(1): testProcDefaultStartedTime,
				process.PID(2): testProcDefaultStartedTime,
				process.PID(3): testProcDefaultStartedTime,
			},
			expectedEvents: []*WatchEvent[ProcessAttrs]{
				{Type: EventCreated, Obj: ProcessAttrs{ID: process.PID(1), StartedTime: testProcDefaultStartedTime}},
				{Type: EventCreated, Obj: ProcessAttrs{ID: process.PID(2), StartedTime: testProcDefaultStartedTime}},
				{Type: EventCreated, Obj: ProcessAttrs{ID: process.PID(3), StartedTime: testProcDefaultStartedTime}},
			},
		},
		"Should send process deleted events": {
			procs: map[process.PID]ProcessAttrs{
				process.PID(1): {ID: process.PID(1), StartedTime: testProcDefaultStartedTime},
				process.PID(2): {ID: process.PID(2), StartedTime: testProcDefaultStartedTime},
				process.PID(3): {ID: process.PID(3), StartedTime: testProcDefaultStartedTime},
			},
			inputPIDs: map[process.PID]time.Time{},
			expectedEvents: []*WatchEvent[ProcessAttrs]{
				{Type: EventDeleted, Obj: ProcessAttrs{ID: process.PID(1), StartedTime: testProcDefaultStartedTime}},
				{Type: EventDeleted, Obj: ProcessAttrs{ID: process.PID(2), StartedTime: testProcDefaultStartedTime}},
				{Type: EventDeleted, Obj: ProcessAttrs{ID: process.PID(3), StartedTime: testProcDefaultStartedTime}},
			},
		},
		"Should send a mix of process created and deleted events": {
			procs: map[process.PID]ProcessAttrs{
				process.PID(1): {ID: process.PID(1), StartedTime: testProcDefaultStartedTime},
			},
			inputPIDs: map[process.PID]time.Time{
				process.PID(2): testProcDefaultStartedTime,
				process.PID(3): testProcDefaultStartedTime,
			},
			expectedEvents: []*WatchEvent[ProcessAttrs]{
				{Type: EventDeleted, Obj: ProcessAttrs{ID: process.PID(1), StartedTime: testProcDefaultStartedTime}},
				{Type: EventCreated, Obj: ProcessAttrs{ID: process.PID(2), StartedTime: testProcDefaultStartedTime}},
				{Type: EventCreated, Obj: ProcessAttrs{ID: process.PID(3), StartedTime: testProcDefaultStartedTime}},
			},
		},
		"Should send process who are old enough to be traced only": {
			procs: map[process.PID]ProcessAttrs{},
			inputPIDs: map[process.PID]time.Time{
				process.PID(1): testProcDefaultStartedTime,
				process.PID(2): time.Now().Add(-1 * time.Second),
				process.PID(3): time.Now().Add(-4 * time.Second),
			},
			expectedEvents: []*WatchEvent[ProcessAttrs]{
				{Type: EventCreated, Obj: ProcessAttrs{ID: process.PID(1), StartedTime: testProcDefaultStartedTime}},
			},
		},
	}

	for tn, tc := range testCases {
		t.Run(tn, func(t *testing.T) {
			t.Parallel()

			processMgr := processmocks.NewManager(t)
			processMgr.EXPECT().ListPIDs().Return(slices.Collect(maps.Keys(tc.inputPIDs)), nil)
			if len(tc.inputPIDs) > 0 {
				processMgr.EXPECT().Attach(mock.Anything).RunAndReturn(func(pid process.PID) (process.Process, error) {
					p := processmocks.NewProcess(t)
					p.EXPECT().CreateTime().Return(tc.inputPIDs[pid].UnixMilli(), nil)
					return p, nil
				})
			}

			outputCh := make(chan []*WatchEvent[ProcessAttrs], 1)
			wg := sync.WaitGroup{}
			ctx, cancel := context.WithCancel(t.Context())
			sut := processWatcher{
				procs:        tc.procs,
				processMgr:   processMgr,
				outputCh:     outputCh,
				pollInterval: 1 * time.Second,
				wg:           &wg,
			}

			wg.Add(1)
			go sut.run(ctx)

			actualEvents := readChannel(t, outputCh, testTimeout)

			assert.Equal(t, len(tc.expectedEvents), len(actualEvents))
			for _, evt := range actualEvents {
				idx := slices.IndexFunc(tc.expectedEvents, func(e *WatchEvent[ProcessAttrs]) bool {
					return e.Obj.ID == evt.Obj.ID
				})
				expectedEvt := tc.expectedEvents[idx]
				assert.Equal(t, expectedEvt.Type, evt.Type)
				assert.EqualValues(t, expectedEvt.Obj, evt.Obj)
			}

			cancel()
			wg.Wait()
		})
	}
}

func TestProcessWatcher_Poll_Should_Not_Send_Events_When_No_Process_Detected(t *testing.T) {
	t.Parallel()

	outputCh := make(chan []*WatchEvent[ProcessAttrs], 1)
	wg := sync.WaitGroup{}
	ctx, cancel := context.WithCancel(t.Context())
	processMgr := processmocks.NewManager(t)
	processMgr.EXPECT().ListPIDs().Return(nil, nil)
	sut := processWatcher{
		procs:        map[process.PID]ProcessAttrs{},
		processMgr:   processMgr,
		outputCh:     outputCh,
		pollInterval: 1 * time.Second,
		wg:           &wg,
	}

	wg.Add(1)
	go sut.run(ctx)

	select {
	case _ = <-outputCh:
		assert.Fail(t, "item received when it should't be the case")
	case <-time.After(time.Second):
		// All good
	}

	cancel()
	wg.Wait()
}

func readChannel[T any](t *testing.T, inCh chan T, timeout time.Duration) T {
	t.Helper()

	var item T

	select {
	case item = <-inCh:
		return item
	case <-time.After(timeout):
		assert.Failf(t, "timeout", "timeout (%s) while waiting for event in input channel", timeout)
	}

	return item
}

package tls

import "io"

type DataPipe struct {
	pr *io.PipeReader
	pw *io.PipeWriter
}

func NewDataPipe() *DataPipe {
	pr, pw := io.Pipe()
	return &DataPipe{pr: pr, pw: pw}
}

func (p *DataPipe) Reader() *io.PipeReader {
	return p.pr
}

func (p *DataPipe) Writer() *io.PipeWriter {
	return p.pw
}

func (p *DataPipe) Close() {
	p.pw.Close()
}

package internal

import (
	"bytes"
	"encoding/json"
	"fmt"

	"k8s.io/client-go/util/jsonpath"
)

func ParsePromptWithJsonPath(payload, jsonPath string) (string, error) {
	jp := jsonpath.New("")
	err := jp.Parse(jsonPath)
	if err != nil {
		return "", fmt.Errorf("failed to parse the JSON path: %s: %w", jsonPath, err)
	}

	var body any
	err = json.Unmarshal([]byte(payload), &body)
	if err != nil {
		return "", fmt.Errorf("failed to unmarshal the payload: %w", err)
	}

	var buf bytes.Buffer
	err = jp.Execute(&buf, body)
	if err != nil {
		return "", fmt.Errorf("failed to find the prompt using the JSON path: %s: %w", jsonPath, err)
	}

	return buf.String(), nil
}

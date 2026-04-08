package main

import (
	"encoding/json"
	"fmt"
)

type App struct {
	BaseURL string
	Name    string
	Type    string
}

func NewAppFromMap(m map[string]any) (*App, error) {
	bytes, err := json.Marshal(m)
	if err != nil {
		return nil, fmt.Errorf("unable to marshal App map to JSON: %w", err)
	}

	var app App

	err = json.Unmarshal(bytes, &app)
	if err != nil {
		return nil, fmt.Errorf("unable to unmarshal App JSON: %w", err)
	}

	return &app, nil
}

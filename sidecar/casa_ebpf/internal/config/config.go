package config

import (
	"fmt"
	"log/slog"

	"github.com/joho/godotenv"
	"github.com/knadh/koanf/parsers/yaml"
	"github.com/knadh/koanf/providers/env/v2"
	"github.com/knadh/koanf/providers/file"
	"github.com/knadh/koanf/v2"
)

type Config struct {
	Discovery DiscoveryConfig `koanf:"discovery"`
}

type DiscoveryConfig struct {
	Criteria []CriteriaAttributes `koanf:"criteria"`
}

type CriteriaAttributes struct {
	TargetPIDs    []uint32 `koanf:"target_pids"`
	ContainerName string   `koanf:"container_name"`
	ContainerID   string   `koanf:"container_id"`
	K8SNamespace  string   `koanf:"k8s_namespace"`
	K8SPodName    string   `koanf:"k8s_pod_name"`
}

func LoadConfig(configPath string) (*Config, error) {
	err := godotenv.Load("./.env")
	if err != nil {
		slog.Debug("No .env file found", "err", err)
	}

	var k = koanf.New(".")

	err = k.Load(file.Provider(configPath), yaml.Parser())
	if err != nil {
		return nil, fmt.Errorf("unable to load config from yaml: %w", err)
	}

	err = k.Load(env.Provider(".", env.Opt{}), nil)
	if err != nil {
		return nil, fmt.Errorf("unable to load config from env: %w", err)
	}

	var conf Config

	err = k.Unmarshal("", &conf)
	if err != nil {
		return nil, fmt.Errorf("unable to unmarshal config: %w", err)
	}

	return &conf, nil
}

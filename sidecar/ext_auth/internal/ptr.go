package internal

func DerefStr(src *string) string {
	return Derefrence(src, "")
}

func Derefrence[T any](src *T, def T) T {
	if src != nil {
		return *src
	}

	return def
}

package main

func ConvertSlice[TSrc, TDst any](src []TSrc, convert func(TSrc) TDst) []TDst {
	out := make([]TDst, len(src))
	for i, v := range src {
		out[i] = convert(v)
	}
	return out
}

func Derefrence[T any](src *T, def T) T {
	if src != nil {
		return *src
	}

	return def
}

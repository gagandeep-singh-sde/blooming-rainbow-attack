package common

import (
	"strings"
)

const (
	PasswordLength    = 4
	ProcessorCores    = 10
	BatchSize         = 1000
	FalsePositiveRate = 0.00001
	CharacterSet      = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789~!@#$%^&*()_+{}|:\"<>?`-=[]\\;',./ "
	TotalCombinations = 1000
	FixedSalt         = "$2b$04$xdBYzsZt7/06MWHpfx8TR."
)

func GetCharacterSet() string {
	return CharacterSet
}

func IsValidPassword(password string) bool {
	hasUpper := false
	hasLower := false
	hasDigit := false
	hasSpecial := false
	for _, c := range password {
		if strings.ContainsRune("ABCDEFGHIJKLMNOPQRSTUVWXYZ", c) {
			hasUpper = true
		} else if strings.ContainsRune("abcdefghijklmnopqrstuvwxyz", c) {
			hasLower = true
		} else if strings.ContainsRune("0123456789", c) {
			hasDigit = true
		} else if strings.ContainsRune("~!@#$%^&*()_+{}|:\"<>?`-=[]\\;',./ ", c) {
			hasSpecial = true
		}
		if hasUpper && hasLower && hasDigit && hasSpecial {
			return true
		}
	}
	return false
}

func Min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

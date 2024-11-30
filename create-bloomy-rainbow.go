package main

import (
	"bufio"
	"fmt"
	"math"
	"os"
	"runtime"
	"strings"
	"sync"
	"time"

	"github.com/bits-and-blooms/bloom/v3"
	"golang.org/x/crypto/bcrypt"
)

const (
	passwordLength    = 4
	processorCores    = 15
	batchSize         = 1000
	falsePositiveRate = 0.00001
	totalCombinations = 10000000
	characterSet      = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789~!@#$%^&*()_+{}|:\"<>?`-=[]\\;',./ "
	fixedSalt         = "$2b$04$xdBYzsZt7/06MWHpfx8TR."
)

func getCharacterSet() string {
	return characterSet
}

func isValidPassword(password string) bool {
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

func processChunk(start, end, chunkIndex int, wg *sync.WaitGroup) {
	defer wg.Done()

	bloomFilter := bloom.NewWithEstimates(uint(batchSize), falsePositiveRate)

	count := 0
	characters := getCharacterSet()
	for i := start; i < end; i++ {
		password := ""
		for j := 0; j < passwordLength; j++ {
			password += string(characters[i%len(characters)])
			i /= len(characters)
		}

		if isValidPassword(password) {
			passwordBytes := []byte(password)
			hashed, _ := bcrypt.GenerateFromPassword(passwordBytes, bcrypt.MinCost)

			bloomFilter.Add(hashed)
			count++
			if count >= batchSize {
				break
			}
		}
	}

	// Save Bloom filter to file
	file, err := os.Create(fmt.Sprintf("bloom_filters/bloom_filter_%d.bloom", chunkIndex))
	if err != nil {
		fmt.Printf("Error creating file: %v\n", err)
		return
	}
	defer file.Close()

	writer := bufio.NewWriter(file)
	if err != nil {
		fmt.Printf("Error writing Bloom filter to file: %v\n", err)
		return
	}
	writer.Flush()
	fmt.Printf("Chunk %d written", chunkIndex)
}

func main() {
	startTime := time.Now()
	numChunks := int(math.Ceil(float64(totalCombinations) / float64(batchSize)))

	var wg sync.WaitGroup
	runtime.GOMAXPROCS(processorCores)

	for i := 0; i < numChunks; i++ {
		start := i * batchSize
		end := (i + 1) * batchSize
		if end > totalCombinations {
			end = totalCombinations
		}
		wg.Add(1)
		go processChunk(start, end, i, &wg)
	}

	wg.Wait()

	elapsedTime := time.Since(startTime)
	fmt.Printf("Total combinations: %d\n", totalCombinations)
	fmt.Printf("Script completed in %.2f seconds\n", elapsedTime.Seconds())
}

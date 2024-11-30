package main

import (
	"bufio"
	"fmt"
	"math"
	"os"
	"runtime"
	"sync"
	"time"

	"goModules/common"

	"github.com/bits-and-blooms/bloom/v3"
	"golang.org/x/crypto/bcrypt"
)

func findHashInBloomFilter(index int, givenHash string) (int, error) {
	file, err := os.Open(fmt.Sprintf("bloom_filters/bloom_filter_%d.bloom", index))
	if err != nil {
		return -1, err
	}
	defer file.Close()

	reader := bufio.NewReader(file)
	var bloomFilter bloom.BloomFilter
	_, err = bloomFilter.ReadFrom(reader)
	if err != nil {
		return -1, err
	}

	if bloomFilter.TestString(givenHash) {
		return index, nil
	}
	return -1, nil
}

func findHashInBloomFilters(givenHash string, numBloomFilters int) []int {
	var foundIndices []int
	var wg sync.WaitGroup
	var mu sync.Mutex

	runtime.GOMAXPROCS(common.ProcessorCores)

	for i := 0; i < numBloomFilters; i++ {
		wg.Add(1)
		go func(index int) {
			defer wg.Done()
			foundIndex, err := findHashInBloomFilter(index, givenHash)
			if err == nil && foundIndex != -1 {
				mu.Lock()
				foundIndices = append(foundIndices, foundIndex)
				mu.Unlock()
			}
		}(i)
	}

	wg.Wait()
	return foundIndices
}

func getPasswordsForHash(givenHash string) []string {
	characters := common.GetCharacterSet()
	totalCombinations := int(math.Pow(float64(len(characters)), float64(common.PasswordLength)))
	numBloomFilters := (totalCombinations + common.BatchSize - 1) / common.BatchSize
	foundIndices := findHashInBloomFilters(givenHash, numBloomFilters)
	var passwords []string

	if len(foundIndices) > 0 {
		for _, index := range foundIndices {
			start := index * common.BatchSize
			end := common.Min((index+1)*common.BatchSize, totalCombinations)
			for i := start; i < end; i++ {
				password := ""
				for j := 0; j < common.PasswordLength; j++ {
					password += string(characters[i%len(characters)])
					i /= len(characters)
				}

				if common.IsValidPassword(password) {
					passwordBytes := []byte(password)
					hashed, _ := bcrypt.GenerateFromPassword(passwordBytes, bcrypt.MinCost)
					if string(hashed) == givenHash {
						passwords = append(passwords, password)
					}
				}
			}
		}
	}
	return passwords
}

func main() {
	startTime := time.Now()
	var givenHash string
	fmt.Print("Enter the hash value: ")
	fmt.Scanln(&givenHash)

	passwords := getPasswordsForHash(givenHash)
	if len(passwords) > 0 {
		for _, password := range passwords {
			fmt.Printf("Password for hash %s: %s\n", givenHash, password)
		}
	} else {
		fmt.Printf("Hash %s not found in any Bloom filter\n", givenHash)
	}

	elapsedTime := time.Since(startTime)
	fmt.Printf("Script completed in %.2f seconds\n", elapsedTime.Seconds())
}

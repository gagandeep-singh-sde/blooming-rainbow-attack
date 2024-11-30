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

func processChunk(start, end, chunkIndex int, wg *sync.WaitGroup) {
	defer wg.Done()

	bloomFilter := bloom.NewWithEstimates(uint(common.BatchSize), common.FalsePositiveRate)

	count := 0
	characters := common.GetCharacterSet()
	for i := start; i < end; i++ {
		password := ""
		for j := 0; j < common.PasswordLength; j++ {
			password += string(characters[i%len(characters)])
			i /= len(characters)
		}

		if common.IsValidPassword(password) {
			passwordBytes := []byte(password)
			hashed, _ := bcrypt.GenerateFromPassword(passwordBytes, bcrypt.MinCost)
			bloomFilter.Add(hashed)
			count++
			if count >= common.BatchSize {
				break
			}
		}
	}

	file, err := os.Create(fmt.Sprintf("bloom_filters/bloom_filter_%d.bloom", chunkIndex))
	if err != nil {
		fmt.Printf("Error creating file: %v\n", err)
		return
	}
	defer file.Close()

	writer := bufio.NewWriter(file)
	bytesWritten, err := bloomFilter.WriteTo(writer)
	if err != nil {
		fmt.Printf("Error writing Bloom filter to file: %v\n", err)
		return
	}
	writer.Flush()
	fmt.Printf("Chunk %d with %d bytes written.\n", chunkIndex, bytesWritten)
}

func main() {
	startTime := time.Now()
	numChunks := int(math.Ceil(float64(common.TotalCombinations) / float64(common.BatchSize)))

	var wg sync.WaitGroup
	runtime.GOMAXPROCS(common.ProcessorCores)

	for i := 0; i < numChunks; i++ {
		start := i * common.BatchSize
		end := (i + 1) * common.BatchSize
		if end > common.TotalCombinations {
			end = common.TotalCombinations
		}
		wg.Add(1)
		go processChunk(start, end, i, &wg)
	}

	wg.Wait()

	elapsedTime := time.Since(startTime)
	fmt.Printf("Total combinations: %d\n", common.TotalCombinations)
	fmt.Printf("Script completed in %.2f seconds\n", elapsedTime.Seconds())
}

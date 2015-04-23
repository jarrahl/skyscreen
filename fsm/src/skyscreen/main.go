package main

import (
	"flag"
	"os"
	"log"
	"github.com/riobard/go-mmap"
	"github.com/rcrowley/go-metrics"
)

func err_panic(err error) {
	if err != nil {
		panic(err)
	}
}

func main() {
	output_file := flag.String("output", "", "output file")
	flag.Parse()
	
	if *output_file == "" {
		panic("Must input a file")
	}

	f, err := os.OpenFile(*output_file, os.O_RDWR, 0)
	err_panic(err)
	memmap, err := mmap.Map(
		f,
		0,
		360*144*2*3,
		mmap.PROT_WRITE,
		mmap.MAP_SHARED)
	err_panic(err)

	go metrics.Log(metrics.DefaultRegistry, 60e7, log.New(os.Stderr, "metrics: ", log.Lmicroseconds))
	m := metrics.NewMeter()
	metrics.Register("fps", m)
	for {
		m.Mark(1)
		for i := 0; i < 360*144*2*3; i += 1 {
			memmap[i] = 255;
		}
	}
}


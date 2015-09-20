#!/bin/bash
mvn compile exec:java -Dstorm.topology=storm.starter.StreamingSearchTopology

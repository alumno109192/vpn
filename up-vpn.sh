#!/bin/bash
resolvectl dns tun0 192.168.253.1
resolvectl domain tun0 "~."
resolvectl default-route tun0 yes

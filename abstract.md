This artifact includes the software used for generating proofs of equivalence
between and totality of regular expressions. It also includes testing
infrastructure for checking these proofs with Metamath Zero.

The benchmarks displayed in the paper are collected by running the `./test`
script. These may then be displayed in (pandoc) markdown using the
`./benchmark-aggregator.py` script. See `README` in archive for details.

These tests have been timed on the TACAS 23 VM running on a 11th Gen Intel(R)
Core(TM) i7-1165G7 host with 32GB of RAM. Default settings were used for
importing the VM into virtualbox, and NAT-based networking was used to install
dependencies.





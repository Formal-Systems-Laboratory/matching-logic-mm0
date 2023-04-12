# Matching Logic in Metamath Zero

This repository represents our efforts to capture the full extent of [Applicative Matching Logic](https://fsl.cs.illinois.edu/publications/chen-rosu-2019-trb.html) in Metamath Zero as well as an axiomatization of the theory of Regular Expressions in Matching Logic.

Moreover, the repository includes a decision procedure that is able to generate machine checkable Metamath Zero proofs for the totality of any regular expression (for now only over a signature composed of two letters: `a` and `b`) in Maude thanks to a technique based on [Brzozowski derivatives](https://dl.acm.org/doi/10.1145/321239.321249).

## Requirements

The minimum requirement to compile and verify the core theory `mm0`/`mm1` files is an installation of the [Metamath Zero](https://github.com/digama0/mm0) toolchain (specifically `mm0-c` and `mm0-rs`). If the user doesn't have these tools installed, they can be easily built locally provided that the user has the following requirements:
* gcc
* Rust

Additionally, in order to run the proof generation procedure, the following need to be installed:
* Maude
* Python

## Installation

## Project Overview

Here we will provide a brief overview of all the files composing this project.

Files with the extension `mm0` are spec files and provide the axiomatization of our theories, and the trust base of our formalisation. All axioms and definitions reside in these files. Files with the extension `mm1`, on the other hand, contain proofs of theorems and automations that make use of the axioms and inference rules described in the `mm0` files. These need not be trusted. They are compiled down to `mmb` files which are the binary proof format that the core Metamath Zero checker, `mm0-c` operates on.

The main decision procedure generating the proofs for regular expressions can be found in `regexp-proof-gen.maude`.

* 00-matching-logic.mm0
* 01-propositional.mm1
* 02-ml-normalization.mm1
* 10-theory-definedness.mm0
* 11-definedness-normalization.mm1
* 12-proof-system-p.mm1
* 13-fixedpoints.mm1
* 20-theory-words.mm0
* 21-words-helpers.mm1
* 23-words-theorems.mm1
* benchmark-agregator.py
* benchmarks.py
* conftest.py
* examples
* maude.py
* poetry.lock
* proof-gen.py
* pyproject.toml
* README.md
* regexp-proof-gen.maude
* test
* test.maude
* test.py

## Running the Test Suite

Running the test suite for this project is as simple as running the `./test` command.

Since some tests take a long time to complete we recommend that users looking to make sure that everything is set up correctly instead run `./test --skip-slow` in order to skip the very slow tests.

If any failure occurs, please report this on the Issues page of this repository.

## Background

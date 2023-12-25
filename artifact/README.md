Matching Logic in Metamath Zero
===============================

This repository represents our efforts to capture the full extent of [Applicative Matching
Logic](https://fsl.cs.illinois.edu/publications/chen-rosu-2019-trb.html) in Metamath Zero as well as
an axiomatization of the theory of Regular Expressions in Matching Logic.

Moreover, the repository includes a decision procedure that is able to generate machine checkable
Metamath Zero proofs for the totality of any regular expression (for now only over a signature
composed of two letters: `a` and `b`) in Maude thanks to a technique based on [Brzozowski
derivatives](https://dl.acm.org/doi/10.1145/321239.321249).

Requirements and Installation
-----------------------------

All the installation instructions are with respect to a Unix based system. For other operating
systems these instructions would have to be adapted.

The minimum requirement to compile and verify the core theory `mm0`/`mm1` files is an installation
of the [Metamath Zero](https://github.com/digama0/mm0) toolchain (specifically `mm0-c` and
`mm0-rs`). If the user doesn’t have these tools installed, they can be easily built inside this
repository by following the instructions below, provided that the user has the following
requirements:

- gcc
- Rust 1.67

Additionally, in order to run the proof generation procedure, the following need to be installed:

- Maude 3.2.1 [^1]
- Python 3.9.13
- Poetry [^2]

The easiest way to install all the tools and requirements of the project is by running:

    ./install.sh

If installing on a Mac, run instead `./install macOS`

This includes building the Metamath Zero toolchain under this repository, installing required Python
modules in a virtual environment via Poetry and selecting an appropriate Maude binary to use.

Running the Test Suite
----------------------

To make sure that everything works correctly, we encourage users to try running the test suite for
this project. Doing this is as simple as running:

    ./test

**Note:** Since some tests take a long time to complete we recommend that users first run
`./test --skip-slow` instead, in order to skip the very slow tests.

If any failure occurs, please report this on the Issues page of this repository.

Project Overview
----------------

Here we will provide a brief overview of the main files composing this project.

Files with the extension `mm0` are spec files and provide the axiomatization of our theories. They
form the trust base of our formalisation. All axioms and definitions reside in these files. Files
with the extension `mm1`, on the other hand, contain proofs of theorems and automations that make
use of the axioms and inference rules described in the `mm0` files. These need not be trusted. They
are compiled down to `mmb` files which are the binary proof format that the core Metamath Zero
checker, `mm0-c` operates on.

The main decision procedure generating the proofs for regular expressions can be found in
`regexp-proof-gen.maude`.

- `_automation.mm1` - This file provides some useful automation for writing `mm1` proofs
- `00-matching-logic.mm0` - This file contains the core axiomatization of (Applicative) Matching
  Logic as well as several useful definitions. It describes the core logic while all other `mm0`
  files only define theories in this logic.
- `01-propositional.mm1` - This file contains theorems of Propositional Logic (which Matching Logic
  subsumes)
- `02-ml-normalization.mm1` - This file contains useful theorems for normalising patterns with
  substitutions, for proving positivity requirements and automation for propagating substitutions
  though a term
- `10-theory-definedness.mm0` - This file axiomatizes the theory of Definedness. This theory is
  needed in order to be able to express equality in Matching Logic.
- `11-definedness-normalization.mm1` - This file contains useful theorems for dealing with the newly
  defined constructs from `10-theory-definedness.mm0`
- `12-proof-system-p.mm1` - This file is the largest `mm1` file and contains proofs for the entirety
  of “Proof System P” as well as many other useful theorems of Matching Logic. It also contains a
  number of meta-theorems in the form of lisp-like programs able to generate proofs via automation.
- `13-fixedpoints.mm1` - This file contains the proofs for the `wrap` and `unwrap` rules dealing
  with contextual implications as well as some theorems about the least fixpoint operator `mu`.
- `20-theory-words.mm0` - This file describes the Matching Logic theory of Regular Expressions. This
  is a shallow embedding and part of the trust base of our formalisation.
- `21-words-helpers.mm1` - This file contains some useful helpers for dealing with this theory of
  Regular Expressions.
- `22-words-theorems.mm1` - This file contains most theorems that the maude generator uses when
  building up a proof. The proof is compiled against these theorems to produce a final `mmb` proof
  object.
- `regexp-proof-gen.maude` - This is the primary maude file that performs the proof search and
  generation. It has rules defined that correspond to theorems in `22-words-theorems.mm1` and is
  applying them strategically, following the algorithm developed by Brozozowski.
- `test` - This is the script used to run our test suite

[^1]: If the user doesn’t have Maude installed on their system, appropriate Maude binaries are
    provided inside this repository for Linux and macOS distributions (see installation instructions
    below).

[^2]: Poetry can be installed by running the following command:

          curl -sSL https://install.python-poetry.org | python3 -

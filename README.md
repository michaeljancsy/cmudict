# CMUdict — ConjureRhyme fork

**This is not pristine CMUdict.** It is a fork of
[cmusphinx/cmudict](https://github.com/cmusphinx/cmudict) carrying a small set of
added pronunciations for [ConjureRhyme](https://github.com/michaeljancsy/prosody),
a prosody and rhyme dictionary. Every addition is listed in
[`conjurerhyme/additions.dict`](conjurerhyme/additions.dict) and applied by script;
nothing else in the dictionary is changed, and nothing is reordered or removed.

If you want the unmodified dictionary, use the `master` branch here — kept as a
clean mirror of upstream — or go to upstream directly.

## Acknowledgement

The Carnegie Mellon Pronouncing Dictionary is Copyright (C) 1993-2015 by Carnegie
Mellon University, maintained by the Speech Group in the School of Computer
Science, and is distributed under the BSD-2-clause-style terms in
[`LICENSE`](LICENSE). CMU's README asks that anyone who uses or redistributes the
material acknowledge its origin; this file, and ConjureRhyme's own README, are
that acknowledgement. Any error in the entries added here is the fork's, not CMU's.

CMU also asks that additions and corrections be sent to them
(air+cmudict@cs.cmu.edu) for consideration in a later version. See "Upstreaming"
below.

## What is added

| entry | reason |
| --- | --- |
| `transplant(2) T R AE1 N S P L AE0 N T` | upstream has only the verb, tranSPLANT; the noun TRANSplant is the commoner sense |
| `transplants(2) T R AE1 N S P L AE0 N T S` | the plural carries the variant, exactly as `transports(2)` does |

Both follow the template upstream already sets for the two closest members of the
same Latinate `trans-` family, which record the verb/noun stress shift in full:

```
transfer     T R AE0 N S F ER1        transport     T R AE0 N S P AO1 R T
transfer(2)  T R AE1 N S F ER0        transport(2)  T R AE1 N S P AO0 R T
transfers    T R AE0 N S F ER1 Z      transports    T R AE0 N S P AO1 R T S
transfers(2) T R AE1 N S F ER0 Z      transports(2) T R AE1 N S P AO0 R T S
```

The verb stays first, as it is for `transfer` and `transport`. Consumers that read
only the first pronunciation of a word therefore see no change at all; picking the
right variant for a context is the consumer's job, not the dictionary's.

## Branches

- **`master`** — a clean mirror of `cmusphinx/cmudict`. Never commit here.
- **`conjurerhyme`** — `master` plus `conjurerhyme/` and the applied additions.
  This is the default branch and the one ConjureRhyme vendors from.

## Applying and re-applying

The dictionary is 3.6 MB of one-entry-per-line text, so additions are kept as data
and merged by script rather than hand-edited:

```sh
python3 conjurerhyme/apply-additions.py            # merge additions into cmudict.dict
python3 conjurerhyme/apply-additions.py --check    # verify only; non-zero if stale
```

Applying twice is a no-op. An entry that upstream has since added itself, with
different phones, is a hard error rather than a silent overwrite.

Each entry is inserted immediately after the last existing pronunciation of its
base word, which is where upstream puts its own variants. The file is deliberately
*not* re-sorted: upstream's order is not any single machine sort (both punctuation
and the `(N)` suffix break a plain byte sort), so re-sorting would produce a diff
of thousands of lines that upstream would never take.

### When upstream releases

```sh
git fetch upstream
git checkout master && git merge --ff-only upstream/master && git push
git checkout conjurerhyme
git checkout upstream/master -- cmudict.dict cmudict.phones cmudict.symbols cmudict.vp LICENSE README README.developer
python3 conjurerhyme/apply-additions.py
git commit -am "Re-apply ConjureRhyme additions over upstream $(git rev-parse --short upstream/master)"
```

Taking the files from `upstream/master` and re-running the script, rather than
rebasing, means an upstream edit near an addition can never conflict: the addition
is re-derived from `additions.dict` against whatever upstream now says.

## Upstreaming

These entries belong upstream, and CMU asks for them. Upstream's cadence is slow
(one or two merges a year), which is why this fork exists rather than a PR alone.
A PR should be cut from `master` with **only** the `cmudict.dict` change — not the
`conjurerhyme/` directory or this file. Taking the file wholesale off the `conjurerhyme`
branch gives exactly that, since the additions are the only thing that differs:

```sh
git checkout -b transplant-noun master
git checkout conjurerhyme -- cmudict.dict
git commit -am "Add the noun stress for transplant and transplants"
git diff master --stat      # should read: 1 file changed, 2 insertions(+)
```

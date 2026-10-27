# FAQ

**Why does an `escaped` not always mean a vulnerability?**
Each escape gets a [reading](../concepts/results.md#readings): `confirmed`, a documented
limit, a design choice, a platform dependency, or an assumption of the contract that does
not hold for that sandbox. Only `confirmed` is a finding.

**Why Linux only?**
The lab image and the published runs are Linux (kernel 6.8, Landlock ABI 4). macOS runs
are next. A contract lists the systems it applies to in `os`.

**Can I trust a result from a sandbox the author maintains?**
Check it. Every case has its raw evidence, the contracts come from other projects' test
suites, and the corpus is versioned by hash, so a contract changed to suit a result shows
up as a new version ([Corpus versions](../concepts/corpus-versions.md)).

**I found a weakness in a sandbox through a contract. Where do I report it?**
To that sandbox's project first. See [`SECURITY.md`](repo:SECURITY.md).

**How do I get my sandbox measured?**
Write its adapter ([Add a sandbox](../how-to/add-a-sandbox.md)) and open a pull request,
or open an issue asking for it.

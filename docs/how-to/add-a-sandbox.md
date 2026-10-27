# Add a sandbox

A sandbox is one module, `runner/adapters/<name>.py`. Nothing else in the engine changes.

```python
NAME = "mysandbox"

def identity():        # name, version, commit, license, artifact_sha256
    ...

def check(contract):   # the policy fields it cannot express: {"unsupported": [...]}
    ...                # or what the lab cannot provide: {"needs_feature": [...]}

def wrap(policy, m, contract, env):   # the argv that runs a phase under the sandbox
    ...
```

The shared policy vocabulary is in [`runner/adapters/common.py`](repo:runner/adapters/common.py),
and the existing adapters are the best examples: [`runner/adapters/sandbox_runtime.py`](repo:runner/adapters/sandbox_runtime.py)
maps to a settings file, [`runner/adapters/landrun.py`](repo:runner/adapters/landrun.py) to flags.

Configure the sandbox the way its own documentation recommends for strict confinement.
An adapter that cannot express a field reports it in `check()`. A policy applied in part
would be a weaker test that reads as a pass.

Then install the sandbox in [`runner/Dockerfile`](repo:runner/Dockerfile), pinned by
version and checked by hash, run it ([Quickstart](../get-started/quickstart.md)), and
write its page in `sandboxes/<name>.md`: what was measured, how each policy field maps,
and what it cannot express. A refusal to start needs a signature the adapter declares,
so the lab can tell a refused policy from a contained attack.

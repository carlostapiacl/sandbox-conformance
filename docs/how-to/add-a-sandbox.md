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

The shared policy vocabulary is in [repo:runner/adapters/common.py](repo:runner/adapters/common.py),
and the existing adapters are the best examples: [repo:runner/adapters/sandbox_runtime.py](repo:runner/adapters/sandbox_runtime.py)
maps to a settings file, [repo:runner/adapters/landrun.py](repo:runner/adapters/landrun.py) to flags.

Configure the sandbox the way its own documentation recommends for strict confinement.
An adapter that cannot express a field reports it, it does not approximate it: a policy
applied partly is a weaker test that reads as a pass.

Then install the sandbox in [repo:runner/Dockerfile](repo:runner/Dockerfile), pinned by
version and checked by hash, run it ([Quickstart](../get-started/quickstart.md)), and
write its page in `sandboxes/<name>.md`: what was measured, how each policy field maps,
and what it cannot express. A refusal to start needs a signature the adapter declares,
so a refused policy reads as a refusal and not as a contained attack.

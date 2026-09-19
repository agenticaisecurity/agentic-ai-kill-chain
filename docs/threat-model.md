# Runnable example: threat model

## Assets and principals

The protected asset is a synthetic credential string in the virtual resource `/workspace/.env`. The legitimate input is `/workspace/src/review_target.py`. These are keys in a Python dictionary, not files opened on the host.

The legitimate task reads the source and publishes a fixed review summary. It is a small task-completion check, not a semantic code-review implementation. The adversary can see the `public-review` output channel. In the conceptual scenario, the adversary controls retrieved repository text; in the executable demonstration, the resulting adversarial actions are supplied directly.

**Instruction delivery and model influence are assumptions, not tested events.** The runnable example begins at the tool invocation boundary.

## Two policies

Both policies permit publishing to `public-review`. The broad policy permits both source and credential reads. The scoped policy permits only the specific source resource. Neither permits arbitrary host access, shell execution or any write tool; those tools do not exist in this implementation.

The virtual tool runtime checks authorization before returning content or publishing output. It uses exact resource allowlists and rejects ambiguous path spellings. No permission increases during the example. The broad-policy disclosure is misuse of existing authority, not privilege escalation.

## Three fixed workloads

1. **Benign:** read source, recognize the example function, publish the fixed review summary. It succeeds under both policies.
2. **Protected-file disclosure:** attempt to read the synthetic credential and publish its contents. It succeeds under broad access and stops at the read check under scoped access.
3. **Residual disclosure:** place the same synthetic marker inside the allowed source, read it and publish it. Both policies permit this. The demo has no content-aware output control.

Each workload uses a fresh runtime and fixture. No output or memory carries between runs. Results contain booleans and policy-decision metadata, not raw resource contents.

## Security boundary and limits

The demonstration assumes the runtime, policy and fixture construction are trusted. An arbitrary Python caller can alter its process; this is not a security boundary against code execution in the interpreter. The meaningful boundary illustrated is whether a supplied tool request receives data under the configured allowlist.

The virtual namespace has no symlinks, hard links, mount points, concurrent filesystem mutation or platform-specific path resolution. Tests against virtual path aliases do not establish resistance to OS filesystem races. Connecting this policy to real tools would require an implementation-specific review and tests.

An allowlisted output destination can still be an unauthorized recipient of particular data. This example makes that fact visible by keeping the attacker-visible review sink allowed under both policies. It does not equate destination allowlisting with data authorization.

The runtime performs no host file reads, network requests, subprocess calls or model calls. The JSON-output command writes only to stdout; shell redirection, if used, writes the selected output file.

The six documented scenarios explore a broader conceptual space. Only the narrow read/publication decision related to the code-review examples is executable here.

## Audit metadata and authority attribution

Decision events use fixed labels for known fixture resources and a constant redaction marker for every other identifier, on allowed as well as denied calls. Invalid-path events also omit the supplied string. This closes direct copying of attacker-controlled path/destination text into the audit resource field. It does not eliminate channels through which choices of actions, labels, denials, counts or timing could encode information. Published content remains intentionally unfiltered so the residual-disclosure case is preserved.

Path syntax and authorization are separate checks. A leading space or fullwidth initial slash fails the absolute-path syntax check; a NEL character (U+0085) is outside the ASCII-control filter and is denied by exact-set membership under the shipped policies. This is a narrow virtual-path grammar, not comprehensive Unicode sanitization.

The runtime uses its configured authority for each named resource. In that sense this demo uses ambient authority (our characterization, not a quotation from Hardy); it does not implement caller-provided capabilities, caller identity, or per-request delegation. See Hardy's [original paper](https://doi.org/10.1145/54289.871709), also available as an [author-text reproduction](https://pdos.csail.mit.edu/6.828/2009/readings/hardy-confused-deputy.html). Scope reduction in this lab should not be mistaken for a capability-based solution to confused delegation.

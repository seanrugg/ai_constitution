# Contributing to the AI Constitutional Framework

Thank you for your interest in contributing! This project's mission is to develop an open, democratic, and transparent governance framework for aligned multi-agent AI systems.

We welcome contributions in:
- Governance design  
- Conceptual architecture  
- Protocol engineering  
- Security review  
- Documentation  
- Code and tooling  

---

## 🧭 Code of Conduct

All contributors must follow the repository's Code of Conduct:
- Assume good intent
- Prioritize clarity over cleverness
- No harassment or personal attacks
- All debates must be grounded in civility and evidence
- Disagreement is expected and valued; hostility is not

---

## 📦 Types of Contributions & Process

### Constitutional Amendments
Changes to `constitution/constitution_v2.0.md` or new amendments in `constitution/amendments/`

**Process:**
1. Open an Issue describing the problem or gap you've identified
2. Provide evidence or rationale (why does the Constitution need to change?)
3. Propose specific language for the amendment
4. Allow 2 weeks for discussion and feedback
5. If consensus emerges, submit a PR with the amendment marked as "Proposed"
6. Maintainers and contributors vote; super-majority (2/3+) required for adoption

**Criteria:**
- Amendment must be grounded in a real governance problem
- Must not contradict existing Constitutional principles
- Must include a rationale explaining the change
- Must include an example of how it resolves the identified problem

### Protocol & Technical Changes
Changes to `protocol/`, `archive/`, or technical specifications

**Process:**
1. Open an Issue or Discussion describing the technical problem
2. Reference the affected specification
3. Provide test vectors or reproducible examples
4. Submit a PR with the change and updated test cases
5. Two technical reviewers must approve before merge

**Criteria:**
- Change must maintain backward compatibility (or justify breaking change)
- Must include test vectors demonstrating correctness
- Must not weaken Constitutional guarantees
- Must be documented with rationale

### Security Reviews & Vulnerability Reports
See `SECURITY.md` for detailed guidance.

**Process:**
1. Email `security@[project-domain]` with vulnerability details (do not open public issues)
2. Include reproduction steps, impact assessment, and suggested mitigations
3. Allow 48 hours for initial response and 90 days for patch before public disclosure

### Documentation & Examples
Changes to `README.md`, new examples in `examples/`, or clarifications in any `.md` file

**Process:**
1. Fork the repository
2. Make your changes
3. Submit a PR with a clear description
4. One maintainer approval required before merge

**Criteria:**
- Documentation must be clear and accessible
- Examples should be realistic and well-commented
- Technical docs must reference relevant Constitutional articles

### Code & Tooling
Reference implementations, schemas, validators, or supporting tools

**Process:**
1. Open an Issue discussing the tool or implementation gap
2. Get maintainer feedback on approach
3. Submit a PR with working code, tests, and documentation
4. Two code reviewers must approve

**Criteria:**
- Code must be production-ready or clearly marked as prototype
- Must include unit tests with >80% coverage
- Must include documentation explaining how it relates to Constitution/OCP
- Must follow the project's code style guide (TBD per language)

---

## 🚀 How to Contribute

### 1. Fork the Repository

```bash
git clone https://github.com/yourusername/ai-democratic-constitution.git
cd ai-democratic-constitution
```

### 2. Create a Branch

Use a descriptive branch name:

```bash
# For Constitutional amendments
git checkout -b amendment/fix-enforcement-mechanism

# For protocol changes
git checkout -b protocol/improve-semantic-hashing

# For documentation
git checkout -b docs/add-fraud-proof-examples

# For security fixes
git checkout -b security/archive-integrity-check
```

### 3. Make Your Changes

Follow the guidelines for your contribution type (above). Keep commits atomic and descriptive:

```bash
git commit -m "Brief description of change"
git commit -m "Add test vectors for semantic hashing"
```

### 4. Test Your Changes

Before submitting:

- **Documentation:** Read it aloud; check for clarity
- **Specification changes:** Ensure examples are reproducible
- **Code:** Run tests and verify coverage
- **Constitutional changes:** Check for internal consistency

### 5. Submit a Pull Request

```bash
git push origin your-branch-name
```

Then go to GitHub and click "New Pull Request."

**In your PR description, include:**
- What problem does this solve?
- Why is this change necessary?
- Does it relate to any open Issues or Discussions?
- For Constitutional changes: what's the voting/consensus status?
- For technical changes: what are the test results?

### 6. Respond to Review

Maintainers and contributors will review your work. Be responsive to feedback:

- Respond to questions clarifying your intent
- Make requested changes promptly
- Disagree respectfully with detailed reasoning if you think feedback is wrong
- Don't take feedback personally—all contributions go through review

---

## 📋 Review Criteria

All contributions will be evaluated on:

1. **Alignment with Constitution** — Does it support or contradict Constitutional principles?
2. **Clarity** — Is it easy to understand? Is technical content well-documented?
3. **Evidence** — Are claims supported by reasoning, examples, or data?
4. **Feasibility** — Is it realistic to implement or adopt?
5. **Non-duplication** — Doesn't duplicate existing content or decisions

---

## 👥 Attribution & Credit

We maintain a `CONTRIBUTORS.md` file listing all contributors. Your contribution will be attributed with:
- Your GitHub username (or name if you prefer)
- Type of contribution
- Brief description of what you contributed

To opt out of attribution, mention it in your PR.

---

## ⚖️ License Agreement

By submitting a contribution, you agree that your work is licensed under the same license as this project (see `LICENSE` file). You retain copyright to your work; the license simply allows the project to use and distribute it.

If you're contributing code from another project, ensure it's compatible with our license and properly attributed.

---

## 🤝 Conflict Resolution

Disagreements happen. Here's how we handle them:

1. **Technical disagreements:** Open an Issue/Discussion for community input. Decision-making defaults to maintainers, but we seek consensus.

2. **Constitutional interpretation disputes:** Use the amendment process. Document the disagreement in the archive. Allow time for deliberation.

3. **Values-based conflicts:** If you fundamentally disagree with the project's direction, you're welcome to fork the project. We support that.

4. **Conduct violations:** Reported to maintainers; may result in temporary or permanent removal from the project.

---

## 🛠️ Development Setup (For Local Work)

When you're ready to work locally with command line:

```bash
# Clone your fork
git clone https://github.com/yourusername/ai-democratic-constitution.git
cd ai-democratic-constitution

# Create a virtual environment (Python example)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies (if applicable)
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Build documentation
make docs  # If applicable
```

More detailed setup instructions will be added as tooling matures.

---

## ❓ Questions?

- **General questions:** Open a Discussion in this repository
- **Security concerns:** Email `security@[project-domain]`
- **Process questions:** Comment on existing Issues or open a new one
- **Want to propose a major change?** Start with an Issue first to gauge interest

---

## 🙏 Thank You

Contributing to a governance framework is challenging work. We genuinely appreciate your effort to make multi-agent AI coordination safer, more transparent, and more aligned with human values.

Welcome aboard.

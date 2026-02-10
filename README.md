# Atomic Design Skill

**Author:** Iván López Hdez · [ivanlopezdev.es](https://ivanlopezdev.es) · [@ivanlhz](https://github.com/ivanlhz)

React component architecture guide following Atomic Design principles. Use it in **any** React project (Vite, Next.js, CRA, Remix, Astro, etc.).

## What's included

- **Component hierarchy**: Atoms → Molecules → Organisms
- **Directory structure**: Where to place shared vs page-specific components
- **Internal structure**: Barrels, styles, tests, types
- **Hooks & Contexts**: Location rules and separation of concerns
- **Logic separation**: Keep components pure, extract logic to custom hooks

## Installation

### Claude Code

Copy `SKILL.md` to your project root as `CLAUDE.md`:

```bash
cp SKILL.md /path/to/your/project/CLAUDE.md
```

Or for global usage across all projects:

```bash
mkdir -p ~/.claude
cp SKILL.md ~/.claude/CLAUDE.md
```

### Cursor

Copy `SKILL.md` to your project's Cursor rules directory:

```bash
mkdir -p /path/to/your/project/.cursor/rules
cp SKILL.md /path/to/your/project/.cursor/rules/atomic-design.md
```

Or configure it globally in Cursor Settings → Rules.

### Claude.ai

Upload `SKILL.md` to your Claude.ai project knowledge base, or reference it in your conversation.

## Usage

Once installed, the AI will:

1. **Follow the structure** when creating new components
2. **Analyze existing code** to detect Atomic Design violations
3. **Suggest refactors** when logic is mixed in components
4. **Place files correctly** based on reusability (shared vs page-specific)

### Example prompts

```
Create a ProductCard molecule with image, title, price, and add to cart button
```

```
Analyze my components folder and check if it follows Atomic Design correctly
```

```
Where should I put a component that's used in both /home and /checkout?
```

## Quick Reference

| Type | Location | Characteristics |
|------|----------|-----------------|
| Atom | `components/atoms/` | Indivisible, no logic, pure UI |
| Molecule | `components/molecules/` | 2-4 atoms, single purpose |
| Organism | `components/organisms/common/` | UI section, cross-page |
| Organism | `components/organisms/[page]/` | UI section, page-specific |
| Hook (generic) | `src/hooks/` | Reusable across components |
| Hook (coupled) | Alongside component | Only used by one component |
| Context | `src/context/` | Always here, cross-component |

## Scripts

### analyze_structure.py

Scans your project and detects Atomic Design violations.

```bash
python scripts/analyze_structure.py ./src
```

**Detects:**
- Missing `atoms/`, `molecules/`, `organisms/` directories
- Components without barrel files (`index.ts`)
- Components without tests
- Logic that should be extracted to hooks (heuristic: >2 hooks + >2 functions)
- Dependency violations (atoms importing from molecules, molecules importing from organisms)

**Example output:**

```
============================================================
  ATOMIC DESIGN ANALYSIS REPORT
============================================================

📦 Components found: 12
✅ With tests: 8/12
📄 With barrels: 10/12

⚙️  Logic in Components (2)
----------------------------------------
  ⚠️ organisms/checkout/CheckoutForm/CheckoutForm.tsx
     Component has 4 hooks and 3 functions. Consider extracting logic to a custom hook.

🔗 Dependency Violations (1)
----------------------------------------
  ❌ atoms/Button/Button.tsx
     Atoms should not import from molecules

------------------------------------------------------------
❌ 1 error(s), 3 warning(s)
```

## License

MIT — see [LICENSE](LICENSE).

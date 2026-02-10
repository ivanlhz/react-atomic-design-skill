---
name: atomic-design
description: React component architecture guide following Atomic Design. ALWAYS USE in React/Next.js/Astro projects to create components, organize folder structure, or decide where to place new components. Also use to ANALYZE existing projects and verify correct Atomic Design implementation, detecting violations like logic in components, incorrect classification (atom vs molecule vs organism), or lack of separation of concerns. Defines atoms/molecules/organisms hierarchy, internal structure, and rules for hooks, contexts, and types.
---

# Atomic Design - Component Architecture

Methodology based on [Brad Frost's Atomic Design](https://atomicdesign.bradfrost.com/chapter-2/) adapted for modern React frameworks.

## Framework Mapping

| Atomic Design | Framework (Next.js/Astro) |
|---------------|---------------------------|
| Atoms         | `components/atoms/`       |
| Molecules     | `components/molecules/`   |
| Organisms     | `components/organisms/`   |
| Templates     | Framework Layouts         |
| Pages         | Router Route Pages        |

## Directory Structure

```
src/
  components/
    atoms/              ← Always shared
    molecules/          ← Always shared
    organisms/
      common/           ← Header, Footer, Sidebar, Modal
      [page]/           ← Page-specific organisms
  hooks/                ← Generic reusable hooks
  context/              ← Contexts (always here, they're cross-component)
  pages/ (or app/)      ← Only route files, layouts, styles
```

## Component Classification

### Atoms
Basic HTML elements that cannot be divided further without losing functionality.

**Examples**: Button, Input, Label, Icon, Logo, Typography, Badge, Avatar, Spinner

**Characteristics**:
- No business logic
- Simple props (variant, size, disabled)
- Reusable in any context

### Molecules
Groups of atoms that function as a unit with a specific purpose.

**Examples**: SearchInput (Label + Input + Button), FormField (Label + Input + ErrorMessage), Card (Image + Title + Description), NavItem (Icon + Label)

**Characteristics**:
- Combine 2-4 atoms
- Single responsibility principle
- Portable and reusable

### Organisms
Complex components that form discrete sections of the interface.

**Examples**: Header, Footer, Sidebar, ProductGrid, CheckoutForm, HeroSection, NavigationMenu

**Characteristics**:
- Combine molecules and/or atoms
- May contain business logic
- Represent complete UI sections

### Organism Placement Rules

```
organisms/
  common/        ← Used across multiple pages (Header, Footer, Modal)
  home/          ← Only used in /home
  checkout/      ← Only used in /checkout
  products/      ← Cross-page by domain (when applicable)
```

**Migration rule**: If a page-specific organism is needed elsewhere, move it to `common/` or create a domain folder if the pattern repeats.

## Internal Component Structure

```
Button/
  Button.tsx           ← Component
  Button.module.css    ← Styles (or .styles.ts for CSS-in-JS)
  Button.test.tsx      ← Tests alongside component
  Button.types.ts      ← Only if types > 30 lines
  index.ts             ← Barrel: export { Button } from './Button'
```

### Type Rules

- **Default**: Types/interfaces in the same `.tsx` file
- **Separate to `.types.ts`**: When exceeding ~30 lines or shared between components

```tsx
// Button.tsx - Simple types, same file
interface ButtonProps {
  variant: 'primary' | 'secondary';
  size: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
}

export const Button = ({ variant, size, children, onClick }: ButtonProps) => {
  // ...
};
```

## Hooks

### Principle: Separate Logic from Presentation

**Component functionality must live in a custom hook, not in the component itself.**

```tsx
// ❌ Bad: Logic mixed in component
const CheckoutForm = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const calculateTotal = () => { /* ... */ };
  const applyDiscount = () => { /* ... */ };
  const submitOrder = async () => { /* ... */ };
  
  return <form>...</form>;
};

// ✅ Good: Logic extracted to hook
const useCheckoutForm = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const calculateTotal = () => { /* ... */ };
  const applyDiscount = () => { /* ... */ };
  const submitOrder = async () => { /* ... */ };
  
  return { items, loading, calculateTotal, applyDiscount, submitOrder };
};

const CheckoutForm = () => {
  const { items, loading, calculateTotal, submitOrder } = useCheckoutForm();
  return <form>...</form>;
};
```

**Benefits**:
- **Testing**: Hook can be tested in isolation with `renderHook()`, no UI rendering needed
- **Reusability**: Logic can be used in another component if needed
- **Readability**: Component becomes pure presentation

**Exception**: Components with trivial logic (a simple `useState`) don't need a separate hook.

### Location

| Type | Location | Example |
|------|----------|---------|
| Generic/reusable | `src/hooks/` | useDebounce, useLocalStorage, useMediaQuery |
| Coupled to component | Alongside component | useCheckoutForm (only used by CheckoutForm) |

**Tests alongside hook:**

```
src/
  hooks/
    useDebounce.ts
    useDebounce.test.ts
    useLocalStorage.ts
    useLocalStorage.test.ts
    useMediaQuery.ts
    useMediaQuery.test.ts
```

### Coupled Hook Example

```
organisms/
  checkout/
    CheckoutForm/
      CheckoutForm.tsx
      CheckoutForm.test.tsx
      useCheckoutForm.ts
      useCheckoutForm.test.ts
      index.ts
```

**Principle**: If the hook exists only to serve a specific component, it lives with it. Delete the component, the hook disappears with it.

## Contexts

**Always in `src/context/`**. Contexts are cross-component by nature.

**Tests alongside context:**

```
src/
  context/
    AuthContext.tsx
    AuthContext.test.tsx
    CartContext.tsx
    CartContext.test.tsx
    ThemeContext.tsx
    ThemeContext.test.tsx
```

## Barrels (index.ts)

Each component exports through its `index.ts`:

```ts
// components/atoms/Button/index.ts
export { Button } from './Button';
export type { ButtonProps } from './Button'; // or from Button.types.ts if separate
```

Optionally, barrel per level:

```ts
// components/atoms/index.ts
export { Button } from './Button';
export { Input } from './Input';
export { Icon } from './Icon';
```

## New Component Checklist

1. **Can it be divided further?** → If not, it's an atom
2. **Does it combine few atoms with one purpose?** → Molecule
3. **Is it a complete UI section?** → Organism
4. **Will it be used across multiple pages?** → `common/` or domain folder
5. **Does it have its own hook that only it uses?** → Hook alongside component
6. **Are types extensive?** → Separate to `.types.ts`

## Complete Example

```
src/
  components/
    atoms/
      Button/
        Button.tsx
        Button.module.css
        Button.test.tsx
        index.ts
      Input/
      Icon/
      index.ts
    molecules/
      SearchInput/
        SearchInput.tsx
        SearchInput.module.css
        SearchInput.test.tsx
        index.ts
      FormField/
      Card/
      index.ts
    organisms/
      common/
        Header/
          Header.tsx
          Header.module.css
          Header.test.tsx
          index.ts
        Footer/
        Sidebar/
      home/
        HeroSection/
        FeaturedGrid/
      checkout/
        CheckoutForm/
          CheckoutForm.tsx
          CheckoutForm.module.css
          CheckoutForm.test.tsx
          useCheckoutForm.ts
          useCheckoutForm.test.ts
          CheckoutForm.types.ts
          index.ts
  hooks/
    useDebounce.ts
    useDebounce.test.ts
    useLocalStorage.ts
    useLocalStorage.test.ts
    useMediaQuery.ts
    useMediaQuery.test.ts
  context/
    AuthContext.tsx
    AuthContext.test.tsx
    CartContext.tsx
    CartContext.test.tsx
```

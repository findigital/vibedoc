# VibeDoc Design System & Style Guide
## Inspired by Monday.com's Award-Winning Design

### 🎨 Design Philosophy

**Core Principles:**
1. **Clarity First** - Every element has a clear purpose
2. **Delightful Interactions** - Smooth, purposeful animations
3. **Bold & Confident** - Strong colors, clear hierarchy
4. **Human & Friendly** - Warm, approachable, conversational
5. **Consistent & Scalable** - Reusable patterns, predictable behavior

---

## Color System

### Primary Palette

```css
/* Primary Brand Colors - Bold & Vibrant */
--primary-500: #6161FF;        /* Main brand color - Electric Purple */
--primary-600: #5151E5;        /* Hover states */
--primary-700: #4141CC;        /* Active states */
--primary-400: #7A7AFF;        /* Light variant */
--primary-300: #9999FF;        /* Lighter variant */

/* Secondary Colors - Success & Energy */
--success-500: #00CA72;        /* Success green */
--success-600: #00B365;        /* Hover */
--success-700: #009954;        /* Active */

--warning-500: #FDAB3D;        /* Warning orange */
--error-500: #E44258;          /* Error red */
--info-500: #0085FF;           /* Info blue */

/* Neutral Colors - Foundation */
--neutral-900: #1F1F1F;        /* Dark text */
--neutral-800: #323338;        /* Secondary text */
--neutral-700: #676879;        /* Tertiary text */
--neutral-500: #C5C7D0;        /* Borders, disabled */
--neutral-300: #E6E9EF;        /* Light borders */
--neutral-100: #F6F7FB;        /* Background light */
--neutral-50: #FFFFFF;         /* Pure white */

/* Accent Colors - Playful Touches */
--accent-purple: #A25DDC;      /* Purple accent */
--accent-pink: #FF6AC3;        /* Pink accent */
--accent-orange: #FF7A59;      /* Orange accent */
--accent-blue: #579BFC;        /* Blue accent */
--accent-teal: #00D4C8;        /* Teal accent */
```

### Color Usage Guidelines

- **Primary**: CTAs, important buttons, links, focus states
- **Success**: Completed actions, positive feedback, pro features
- **Warning**: Cautionary information, approaching limits
- **Error**: Error states, destructive actions, limit reached
- **Neutral**: Text, borders, backgrounds, disabled states
- **Accents**: Feature highlights, tags, categories, illustrations

---

## Typography

### Font Families

```css
/* Primary Font - Display & Body */
--font-primary: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont,
                'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell',
                sans-serif;

/* Monospace - Code & Technical */
--font-mono: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
```

### Type Scale

```css
/* Headings */
--text-6xl: 3.75rem;    /* 60px - Hero */
--text-5xl: 3rem;       /* 48px - Page titles */
--text-4xl: 2.25rem;    /* 36px - Section titles */
--text-3xl: 1.875rem;   /* 30px - Card titles */
--text-2xl: 1.5rem;     /* 24px - Subsections */
--text-xl: 1.25rem;     /* 20px - Large body */

/* Body */
--text-lg: 1.125rem;    /* 18px - Large body */
--text-base: 1rem;      /* 16px - Default body */
--text-sm: 0.875rem;    /* 14px - Small text */
--text-xs: 0.75rem;     /* 12px - Captions */

/* Weights */
--font-light: 300;
--font-regular: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;
```

---

## Spacing System

### Base Unit: 4px

```css
--space-1: 0.25rem;     /* 4px */
--space-2: 0.5rem;      /* 8px */
--space-3: 0.75rem;     /* 12px */
--space-4: 1rem;        /* 16px */
--space-5: 1.25rem;     /* 20px */
--space-6: 1.5rem;      /* 24px */
--space-8: 2rem;        /* 32px */
--space-10: 2.5rem;     /* 40px */
--space-12: 3rem;       /* 48px */
--space-16: 4rem;       /* 64px */
--space-20: 5rem;       /* 80px */
--space-24: 6rem;       /* 96px */
```

---

## Shadows & Depth

```css
/* Elevation System */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
             0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
             0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
             0 10px 10px -5px rgba(0, 0, 0, 0.04);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

/* Colored Shadows for Depth */
--shadow-primary: 0 10px 30px -5px rgba(97, 97, 255, 0.3);
--shadow-success: 0 10px 30px -5px rgba(0, 202, 114, 0.3);
```

---

## Border Radius

```css
--radius-sm: 0.25rem;    /* 4px - Tags, badges */
--radius-md: 0.5rem;     /* 8px - Buttons, inputs */
--radius-lg: 0.75rem;    /* 12px - Cards */
--radius-xl: 1rem;       /* 16px - Large cards */
--radius-2xl: 1.5rem;    /* 24px - Special elements */
--radius-full: 9999px;   /* Pills, avatars */
```

---

## Animation & Transitions

### Timing Functions

```css
--ease-smooth: cubic-bezier(0.4, 0.0, 0.2, 1);        /* Default smooth */
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55); /* Playful bounce */
--ease-swift: cubic-bezier(0.4, 0.0, 0.6, 1);         /* Quick in-out */
```

### Duration

```css
--duration-fast: 150ms;      /* Quick feedback */
--duration-normal: 250ms;    /* Standard transitions */
--duration-slow: 350ms;      /* Emphasized animations */
--duration-slower: 500ms;    /* Page transitions */
```

### Common Animations

```css
/* Fade In */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Slide Up */
@keyframes slideUp {
  from { transform: translateY(10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Scale In */
@keyframes scaleIn {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

/* Pulse */
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* Shimmer (Loading) */
@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}
```

---

## Component Patterns

### Buttons

**Primary Button**
- Background: `--primary-500`
- Hover: `--primary-600` + slight scale (1.02)
- Active: `--primary-700` + scale (0.98)
- Shadow: `--shadow-md` → `--shadow-lg` on hover
- Border radius: `--radius-md`
- Padding: `12px 24px`
- Transition: all `--duration-normal` `--ease-smooth`

**Secondary Button**
- Background: transparent
- Border: 2px solid `--neutral-300`
- Hover: Background `--neutral-100`
- Text color: `--neutral-800`

**Danger Button**
- Background: `--error-500`
- Similar interaction to primary

### Cards

```css
.card {
  background: var(--neutral-50);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--space-6);
  transition: all var(--duration-normal) var(--ease-smooth);
}

.card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}
```

### Inputs

```css
.input {
  border: 2px solid var(--neutral-300);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-base);
  transition: all var(--duration-fast) var(--ease-smooth);
}

.input:focus {
  border-color: var(--primary-500);
  box-shadow: 0 0 0 4px rgba(97, 97, 255, 0.1);
  outline: none;
}
```

---

## Micro-Interactions

### 1. Button Click Ripple
- Circular ripple effect from click point
- Color: white at 20% opacity
- Duration: 600ms

### 2. Loading Skeleton
- Shimmer animation across content
- Gradient: light gray to slightly darker
- Speed: 2s infinite

### 3. Success Checkmark
- Scale in with bounce
- Rotate slightly for playfulness
- Green check icon with circular background

### 4. Toast Notifications
- Slide in from top-right
- Auto-dismiss after 4s
- Swipe to dismiss gesture

### 5. Progress Indicators
- Smooth animated fill
- Percentage counter counts up
- Color changes based on completion (orange → green)

### 6. Form Validation
- Real-time validation with smooth transitions
- Error shake animation
- Success slide-in checkmark

### 7. Hover States
- Slight scale increase (1.02-1.05)
- Shadow enhancement
- Color brightening
- Cursor changes

---

## Layout Patterns

### Container Widths

```css
--container-sm: 640px;
--container-md: 768px;
--container-lg: 1024px;
--container-xl: 1280px;
--container-2xl: 1536px;
```

### Grid System

- 12-column grid
- Gutters: 24px (--space-6)
- Responsive breakpoints: 640px, 768px, 1024px, 1280px

### Common Layouts

1. **Dashboard Layout**
   - Sidebar navigation (280px fixed)
   - Main content (flexible)
   - Top bar (64px fixed)

2. **Card Grid**
   - 3 columns on desktop
   - 2 columns on tablet
   - 1 column on mobile
   - Gap: 24px

3. **Form Layout**
   - Max width: 600px
   - Centered
   - Fields full-width
   - Labels above inputs

---

## Accessibility

### Focus States

```css
*:focus-visible {
  outline: 3px solid var(--primary-500);
  outline-offset: 2px;
}
```

### Color Contrast

- Text on white: Minimum AA (4.5:1)
- Large text: Minimum AA (3:1)
- Interactive elements: Clear visual feedback

### Motion

- Respect `prefers-reduced-motion`
- Disable animations when requested

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Icon System

### Icon Size Scale

```css
--icon-xs: 12px;
--icon-sm: 16px;
--icon-md: 20px;
--icon-lg: 24px;
--icon-xl: 32px;
--icon-2xl: 48px;
```

### Icon Library

Use: **Lucide Icons** or **Heroicons**
- Consistent stroke width (2px)
- Rounded corners
- 24x24 base canvas

---

## Messaging & Copy

### Voice & Tone

- **Friendly**: "Let's create something amazing!"
- **Encouraging**: "You're on a roll! 🎉"
- **Clear**: "Generate your first plan to get started"
- **Helpful**: "Need help? We're here for you"

### Error Messages

- ❌ Bad: "Error 403"
- ✅ Good: "Oops! You've reached your monthly limit. Upgrade to keep creating."

### Empty States

- Icon + Heading + Description + CTA
- Example: "No projects yet. Let's create your first one!"

---

## Gradio-Specific Adaptations

### Custom CSS Classes

```css
.vibedoc-primary-btn { /* Primary button styling */ }
.vibedoc-card { /* Card styling */ }
.vibedoc-input { /* Input styling */ }
.vibedoc-success { /* Success states */ }
.vibedoc-error { /* Error states */ }
```

### Component Overrides

1. **Buttons**: Override Gradio defaults with custom classes
2. **Textboxes**: Custom focus states and borders
3. **Markdown**: Custom typography and spacing
4. **Tabs**: Modern tab design with active indicators

---

## Implementation Checklist

- [ ] Define CSS custom properties
- [ ] Create Gradio custom theme
- [ ] Implement button components
- [ ] Style form inputs
- [ ] Design card layouts
- [ ] Add animations
- [ ] Create loading states
- [ ] Design pricing cards
- [ ] Implement toast notifications
- [ ] Add progress indicators
- [ ] Test accessibility
- [ ] Responsive testing

---

## Resources

- **Color Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Animation Inspiration**: https://www.framer.com/motion/
- **Icon Library**: https://lucide.dev/
- **Typography**: https://fonts.google.com/specimen/Inter

---

**Version**: 1.0.0
**Last Updated**: 2025-11-11
**Maintained by**: VibeDoc Design Team

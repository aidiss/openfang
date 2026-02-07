# DOM Manipulation

Functions for manipulating DOM elements including class management, content swapping, and element removal with animation support.

## Capabilities

### Element Removal

Removes elements from the DOM with optional delay for animations.

```javascript { .api }
/**
 * Removes an element from the DOM
 * @param elt - Element to remove
 * @param delay - Optional delay in milliseconds before removal
 */
function remove(elt: Node, delay?: number): void;
```

**Usage Examples:**

```javascript
// Immediate removal
const element = document.getElementById('temp-message');
htmx.remove(element);

// Delayed removal (useful for animations)
const notification = document.querySelector('.notification');
htmx.remove(notification, 3000); // Remove after 3 seconds

// Remove with CSS animation
const card = document.getElementById('card-123');
card.classList.add('fade-out'); // Add fade-out animation class
htmx.remove(card, 500); // Remove after animation completes

// Remove multiple elements
const errorMessages = document.querySelectorAll('.error-message');
errorMessages.forEach(msg => {
  htmx.remove(msg, 2000);
});
```

### CSS Class Management

Add, remove, and toggle CSS classes with optional delays for animations.

```javascript { .api }
/**
 * Adds a class to the given element
 * @param elt - Target element or CSS selector
 * @param clazz - Class name to add
 * @param delay - Optional delay in milliseconds
 */
function addClass(elt: Element | string, clazz: string, delay?: number): void;

/**
 * Removes a class from the given element
 * @param node - Target element or CSS selector  
 * @param clazz - Class name to remove
 * @param delay - Optional delay in milliseconds
 */
function removeClass(node: Node | string, clazz: string, delay?: number): void;

/**
 * Toggles the given class on an element
 * @param elt - Target element or CSS selector
 * @param clazz - Class name to toggle
 */
function toggleClass(elt: Element | string, clazz: string): void;
```

**Usage Examples:**

```javascript
// Add class immediately
htmx.addClass('#message', 'visible');
htmx.addClass(document.getElementById('panel'), 'expanded');

// Add class with delay
htmx.addClass('.loading-spinner', 'active', 1000);

// Remove class
htmx.removeClass('#dialog', 'hidden');
htmx.removeClass('.button', 'disabled', 500);

// Toggle class
htmx.toggleClass('#menu', 'open');
htmx.toggleClass('.theme-switcher', 'dark-mode');

// Animation sequences
const button = document.getElementById('save-button');
htmx.addClass(button, 'loading');
// ... perform save operation ...
htmx.removeClass(button, 'loading');
htmx.addClass(button, 'success', 100);
htmx.removeClass(button, 'success', 2000);
```

### Class Taking

Ensures only a specific element has a class among its siblings.

```javascript { .api }
/**
 * Takes the given class from siblings (ensures only this element has the class)
 * @param elt - Target element or CSS selector
 * @param clazz - Class name to take from siblings
 */
function takeClass(elt: Node | string, clazz: string): void;
```

**Usage Examples:**

```javascript
// Tab selection - only one tab can be active
const activeTab = document.getElementById('tab-2');
htmx.takeClass(activeTab, 'active'); // Removes 'active' from siblings, adds to this element

// Navigation menu
htmx.takeClass('#nav-home', 'current-page');

// Card selection in a grid
const selectedCard = document.querySelector('.card[data-id="123"]');
htmx.takeClass(selectedCard, 'selected');

// Radio button-like behavior for custom elements
document.addEventListener('click', function(event) {
  if (event.target.matches('.custom-radio')) {
    htmx.takeClass(event.target, 'checked');
  }
});

// Accordion panels - only one can be expanded
function expandPanel(panelId) {
  const panel = document.getElementById(panelId);
  htmx.takeClass(panel, 'expanded');
}
```

### Content Swapping

Performs complete content replacement with the full htmx swapping pipeline including transitions and focus management.

```javascript { .api }
/**
 * Implements complete swapping pipeline including transitions, focus preservation, etc.
 * @param target - Target element or CSS selector
 * @param content - HTML content to swap in
 * @param swapSpec - Swap specification object
 * @param swapOptions - Optional swap options
 */
function swap(target: string | Element, content: string, swapSpec: HtmxSwapSpecification, swapOptions?: SwapOptions): void;

interface HtmxSwapSpecification {
  swapStyle: HtmxSwapStyle;
  swapDelay: number;
  settleDelay: number;
  transition?: boolean;
  ignoreTitle?: boolean;
  head?: string;
  scroll?: "top" | "bottom" | number;
  scrollTarget?: string;
  show?: string;
  showTarget?: string;
  focusScroll?: boolean;
}

interface SwapOptions {
  select?: string;
  selectOOB?: string;
  eventInfo?: any;
  anchor?: string;
  contextElement?: Element;
  afterSwapCallback?: swapCallback;
  afterSettleCallback?: swapCallback;
  beforeSwapCallback?: swapCallback;
  title?: string;
  historyRequest?: boolean;
}

type HtmxSwapStyle = "innerHTML" | "outerHTML" | "beforebegin" | "afterbegin" | "beforeend" | "afterend" | "delete" | "none" | string;
type swapCallback = () => any;
```

**Basic Swap Examples:**

```javascript
// Simple innerHTML replacement
htmx.swap('#content', '<h1>New Content</h1>', {
  swapStyle: 'innerHTML',
  swapDelay: 0,
  settleDelay: 20
});

// Replace entire element
htmx.swap('#old-element', '<div id="new-element">Updated</div>', {
  swapStyle: 'outerHTML',
  swapDelay: 0,
  settleDelay: 20
});

// Append content
htmx.swap('#list', '<li>New Item</li>', {
  swapStyle: 'beforeend',
  swapDelay: 0,
  settleDelay: 20
});

// Prepend content
htmx.swap('#notifications', '<div class="alert">New notification</div>', {
  swapStyle: 'afterbegin',
  swapDelay: 100,
  settleDelay: 50
});
```

**Advanced Swap Examples:**

```javascript
// Swap with transition effects
htmx.swap('#panel', '<div class="panel-content">Updated content</div>', {
  swapStyle: 'innerHTML',
  swapDelay: 200,
  settleDelay: 300,
  transition: true
}, {
  beforeSwapCallback: () => {
    console.log('About to swap content');
  },
  afterSwapCallback: () => {
    console.log('Content swapped');
  },
  afterSettleCallback: () => {
    console.log('Swap settled');
    // Initialize new content
    initializeNewComponents();
  }
});

// Swap with scrolling
htmx.swap('#main-content', newPageContent, {
  swapStyle: 'innerHTML',
  swapDelay: 0,
  settleDelay: 20,
  scroll: 'top',
  focusScroll: true
}, {
  title: 'New Page Title'
});

// Conditional swapping based on content
function smartSwap(target, content) {
  const swapSpec = {
    swapStyle: 'innerHTML',
    swapDelay: 0,
    settleDelay: 20
  };
  
  const swapOptions = {
    beforeSwapCallback: () => {
      // Add loading state
      htmx.addClass(target, 'loading');
    },
    afterSwapCallback: () => {
      // Remove loading state
      htmx.removeClass(target, 'loading');
    },
    afterSettleCallback: () => {
      // Announce to screen readers
      const announcement = document.createElement('div');
      announcement.setAttribute('role', 'status');
      announcement.setAttribute('aria-live', 'polite');
      announcement.textContent = 'Content updated';
      document.body.appendChild(announcement);
      
      setTimeout(() => htmx.remove(announcement), 1000);
    }
  };
  
  htmx.swap(target, content, swapSpec, swapOptions);
}
```

### Out-of-Band Swaps

Handle content that needs to be swapped into different parts of the page.

```javascript
// Process out-of-band content from server response
function handleOOBContent(responseHTML) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(responseHTML, 'text/html');
  
  // Find elements with hx-swap-oob attribute
  const oobElements = doc.querySelectorAll('[hx-swap-oob]');
  
  oobElements.forEach(element => {
    const oobSpec = element.getAttribute('hx-swap-oob');
    const [swapStyle, target] = oobSpec.split(':');
    
    const targetElement = target ? document.querySelector(target) : 
                         document.getElementById(element.id);
    
    if (targetElement) {
      htmx.swap(targetElement, element.outerHTML, {
        swapStyle: swapStyle || 'innerHTML',
        swapDelay: 0,
        settleDelay: 20
      });
    }
  });
}

// Manual out-of-band swap
function updateSidebar(content) {
  htmx.swap('#sidebar', content, {
    swapStyle: 'innerHTML',
    swapDelay: 0,
    settleDelay: 20
  }, {
    selectOOB: '#sidebar-content',
    afterSettleCallback: () => {
      // Reinitialize sidebar components
      initializeSidebar();
    }
  });
}
```

## Animation Integration 

Coordinating DOM manipulation with CSS animations and transitions.

### CSS Animation Patterns

```javascript
// Fade in new content
function fadeInContent(target, content) {
  htmx.swap(target, content, {
    swapStyle: 'innerHTML',
    swapDelay: 0,
    settleDelay: 20
  }, {
    afterSwapCallback: () => {
      htmx.addClass(target, 'fade-in');
    },
    afterSettleCallback: () => {
      // Remove animation class after animation completes
      setTimeout(() => {
        htmx.removeClass(target, 'fade-in');
      }, 300);
    }
  });
}

// Slide animation sequence
function slideReplaceContent(target, content) {
  // Slide out current content
  htmx.addClass(target, 'slide-out');
  
  // Replace content after slide-out animation
  setTimeout(() => {
    htmx.swap(target, content, {
      swapStyle: 'innerHTML',
      swapDelay: 0,
      settleDelay: 20
    }, {
      afterSwapCallback: () => {
        htmx.removeClass(target, 'slide-out');
        htmx.addClass(target, 'slide-in');
      },
      afterSettleCallback: () => {
        setTimeout(() => {
          htmx.removeClass(target, 'slide-in');
        }, 300);
      }
    });
  }, 300);
}
```

### JavaScript Animation Integration

```javascript
// Web Animations API integration
function animatedSwap(target, content, animation = 'fadeIn') {
  const element = typeof target === 'string' ? document.querySelector(target) : target;
  
  const animations = {
    fadeIn: [
      { opacity: 0 },
      { opacity: 1 }
    ],
    slideUp: [
      { transform: 'translateY(20px)', opacity: 0 },
      { transform: 'translateY(0)', opacity: 1 }
    ],
    scale: [
      { transform: 'scale(0.8)', opacity: 0 },
      { transform: 'scale(1)', opacity: 1 }
    ]
  };
  
  htmx.swap(element, content, {
    swapStyle: 'innerHTML',
    swapDelay: 0,
    settleDelay: 20
  }, {
    afterSwapCallback: () => {
      element.animate(animations[animation], {
        duration: 300,
        easing: 'ease-out',
        fill: 'both'
      });
    }
  });
}

// GSAP integration example
function gsapSwap(target, content) {
  const element = typeof target === 'string' ? document.querySelector(target) : target;
  
  // Animate out current content
  gsap.to(element, {
    opacity: 0,
    y: -20,
    duration: 0.2,
    onComplete: () => {
      // Swap content
      htmx.swap(element, content, {
        swapStyle: 'innerHTML',
        swapDelay: 0,
        settleDelay: 20
      }, {
        afterSwapCallback: () => {
          // Animate in new content
          gsap.fromTo(element, 
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.3 }
          );
        }
      });
    }
  });
}
```

## Accessibility Considerations

DOM manipulation with accessibility in mind.

```javascript
// Announce content changes to screen readers
function accessibleSwap(target, content, announcement) {
  htmx.swap(target, content, {
    swapStyle: 'innerHTML',
    swapDelay: 0,
    settleDelay: 20
  }, {
    afterSettleCallback: () => {
      // Create announcement for screen readers
      const announcer = document.createElement('div');
      announcer.setAttribute('aria-live', 'polite');
      announcer.setAttribute('aria-atomic', 'true');
      announcer.className = 'sr-only';
      announcer.textContent = announcement || 'Content updated';
      
      document.body.appendChild(announcer);
      
      // Clean up announcement
      setTimeout(() => htmx.remove(announcer), 1000);
      
      // Manage focus if needed
      const newFocusTarget = document.querySelector(target + ' [autofocus]');
      if (newFocusTarget) {
        newFocusTarget.focus();
      }
    }
  });
}

// Preserve focus context during swaps
function focusAwareSwap(target, content) {
  const activeElement = document.activeElement;
  const focusPath = getFocusPath(activeElement);
  
  htmx.swap(target, content, {
    swapStyle: 'innerHTML',
    swapDelay: 0,
    settleDelay: 20
  }, {
    afterSettleCallback: () => {
      // Attempt to restore focus
      restoreFocus(focusPath) || focusFirstInteractive(target);
    }
  });
}

function getFocusPath(element) {
  const path = [];
  let current = element;
  
  while (current && current !== document.body) {
    if (current.id) {
      path.unshift('#' + current.id);
      break;
    } else if (current.className) {
      path.unshift('.' + current.className.split(' ')[0]);
    }
    current = current.parentElement;
  }
  
  return path.join(' ');
}

function restoreFocus(focusPath) {
  if (!focusPath) return false;
  
  const element = document.querySelector(focusPath);
  if (element && element.focus) {
    element.focus();
    return true;
  }
  return false;
}

function focusFirstInteractive(container) {
  const target = typeof container === 'string' ? document.querySelector(container) : container;
  const focusable = target.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
  
  if (focusable) {
    focusable.focus();
  }
}
```
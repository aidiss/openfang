# DOM Querying

Utility functions for finding and querying DOM elements with htmx-aware selectors and value resolution capabilities.

## Capabilities

### Find Single Element

Finds the first element matching a CSS selector, with flexible calling patterns.

```javascript { .api }
/**
 * Finds an element matching the selector
 * @param eltOrSelector - Root element or CSS selector to search from
 * @param selector - CSS selector when first argument is an element
 * @returns First matching element or null if not found
 */
function find(eltOrSelector: ParentNode | string, selector?: string): Element | null;
```

**Usage Examples:**

```javascript
// Find by selector from document root
const button = htmx.find('#submit-button');
const firstInput = htmx.find('input[type="text"]');

// Find within specific element
const form = document.getElementById('user-form');
const emailInput = htmx.find(form, 'input[name="email"]');

// Find with complex selectors
const activeButton = htmx.find('.button.active:not(.disabled)');
const dataElement = htmx.find('[data-user-id="123"]');

// Chain with null checking
const button = htmx.find('#my-button');
if (button) {
  button.textContent = 'Found!';
}
```

### Find All Elements

Finds all elements matching a CSS selector, returning a NodeList.

```javascript { .api }
/**
 * Finds all elements matching the selector
 * @param eltOrSelector - Root element or CSS selector to search from  
 * @param selector - CSS selector when first argument is an element
 * @returns NodeList of all matching elements
 */
function findAll(eltOrSelector: ParentNode | string, selector?: string): NodeListOf<Element>;
```

**Usage Examples:**

```javascript
// Find all elements by selector
const allButtons = htmx.findAll('button');
const requiredInputs = htmx.findAll('input[required]');

// Find within container
const container = document.getElementById('form-container');
const allInputs = htmx.findAll(container, 'input, textarea, select');

// Iterate over results
const errorElements = htmx.findAll('.error');
errorElements.forEach(element => {
  element.style.display = 'none';
});

// Convert NodeList to Array for advanced operations
const buttons = Array.from(htmx.findAll('button.dynamic'));
const disabledButtons = buttons.filter(btn => btn.disabled);

// Count elements
const itemCount = htmx.findAll('.item').length;
console.log(`Found ${itemCount} items`);
```

### Find Closest Ancestor

Finds the closest ancestor element matching a selector, traversing up the DOM tree.

```javascript { .api }
/**
 * Finds the closest matching element in the parentage
 * @param elt - Starting element or CSS selector
 * @param selector - CSS selector to match against ancestors
 * @returns Closest matching ancestor element or null
 */
function closest(elt: Element | string, selector: string): Element | null;
```

**Usage Examples:**

```javascript
// Find closest form from input element
const input = document.getElementById('user-name');
const form = htmx.closest(input, 'form');

// Find closest container with specific class
const button = htmx.find('#action-button');
const card = htmx.closest(button, '.card');

// Find data container
const clickedElement = event.target;
const dataContainer = htmx.closest(clickedElement, '[data-user-id]');
if (dataContainer) {
  const userId = dataContainer.getAttribute('data-user-id');
  console.log('User ID:', userId);
}

// Find closest with multiple possible selectors
const element = htmx.find('#some-element');
const container = htmx.closest(element, '.container, .wrapper, .main');

// Use with event delegation
document.addEventListener('click', function(event) {
  const button = htmx.closest(event.target, 'button');
  if (button) {
    console.log('Button clicked:', button.textContent);
  }
});
```

### Value Resolution  

Retrieves input values using htmx's value resolution mechanism, which includes form data, element values, and custom value sources.

```javascript { .api }
/**
 * Returns input values that would resolve for a given element via htmx value resolution
 * @param elt - Element to resolve values on
 * @param type - Request type (e.g., 'get' or 'post'). Non-GET requests include enclosing form
 * @returns Object containing resolved values
 */
function values(elt: Element, type: HttpVerb): Object;

type HttpVerb = "get" | "head" | "post" | "put" | "delete" | "connect" | "options" | "trace" | "patch";
```

**Usage Examples:**

```javascript
// Get form values for POST request (includes all form inputs)
const form = document.getElementById('user-form');
const formData = htmx.values(form, 'post');
console.log('Form data:', formData);
// Output: { name: 'John', email: 'john@example.com', age: '30' }

// Get values for GET request (typically just the element itself)
const input = document.getElementById('search-input');
const searchData = htmx.values(input, 'get');
console.log('Search data:', searchData);

// Get values from container with multiple inputs
const container = document.getElementById('filters');
const filterData = htmx.values(container, 'post');
console.log('Filter data:', filterData);

// Include values from elements with hx-include
const button = document.getElementById('submit-btn');
// If button has hx-include="#extra-data", those values are included
const allData = htmx.values(button, 'post');

// Work with complex form structures
const complexForm = document.getElementById('nested-form');
const nestedData = htmx.values(complexForm, 'post');
// Includes nested fieldsets, disabled inputs (if enabled), etc.
```

## Advanced Querying Patterns

### Combining Query Functions

Effective patterns for combining the query functions for complex DOM operations.

```javascript
// Find and validate pattern
function findAndValidate(selector, validator) {
  const elements = htmx.findAll(selector);
  return Array.from(elements).filter(validator);
}

// Find required inputs that are empty
const emptyRequired = findAndValidate('input[required]', el => !el.value.trim());

// Find forms with errors
const formsWithErrors = findAndValidate('form', form => {
  return htmx.findAll(form, '.error').length > 0;
});

// Closest data container pattern
function getDataContainer(element) {
  return htmx.closest(element, '[data-id], [data-user-id], [data-item-id]');
}

// Multi-level search pattern
function findInContainer(containerId, selector) {
  const container = htmx.find(`#${containerId}`);
  return container ? htmx.findAll(container, selector) : [];
}

// Usage
const containerInputs = findInContainer('user-settings', 'input, select');
```

### Event Delegation with Querying

Using htmx querying functions for effective event delegation.

```javascript
// Generic event delegation handler
document.addEventListener('click', function(event) {
  // Check for different types of clickable elements
  const button = htmx.closest(event.target, 'button, [role="button"]');
  const link = htmx.closest(event.target, 'a[href]');
  const formControl = htmx.closest(event.target, 'input, select, textarea');
  
  if (button) {
    handleButtonClick(button, event);
  } else if (link) {
    handleLinkClick(link, event);
  } else if (formControl) {
    handleFormControlInteraction(formControl, event);
  }
});

function handleButtonClick(button, event) {
  // Find associated form or data container
  const form = htmx.closest(button, 'form');
  const dataContainer = htmx.closest(button, '[data-action]');
  
  if (form && button.type === 'submit') {
    // Handle form submission
    const formData = htmx.values(form, 'post');
    console.log('Submitting form:', formData);
  } else if (dataContainer) {
    const action = dataContainer.getAttribute('data-action');
    console.log('Performing action:', action);
  }
}
```

### Dynamic Content Handling

Querying patterns for dynamically loaded content.

```javascript
// Wait for content to load then query
htmx.on('htmx:afterSwap', function(event) {
  const newContent = event.target;
  
  // Find elements in new content
  const newButtons = htmx.findAll(newContent, 'button[data-action]');
  const newForms = htmx.findAll(newContent, 'form[data-validate]');
  
  // Initialize new elements
  newButtons.forEach(button => {
    initializeButton(button);
  });
  
  newForms.forEach(form => {
    initializeFormValidation(form);
  });
});

// Progressive enhancement pattern
function enhanceContent(container) {
  // Find all enhanceable elements
  const tooltips = htmx.findAll(container, '[data-tooltip]');
  const modals = htmx.findAll(container, '[data-modal]');
  const accordions = htmx.findAll(container, '[data-accordion]');
  
  // Enhance each type
  tooltips.forEach(initializeTooltip);
  modals.forEach(initializeModal);
  accordions.forEach(initializeAccordion);
}

// Run on initial load and after htmx swaps
document.addEventListener('DOMContentLoaded', () => enhanceContent(document.body));
htmx.on('htmx:load', (event) => enhanceContent(event.target));
```

### Form Processing Patterns

Specialized patterns for working with forms and form data.

```javascript
// Comprehensive form data collection
function collectFormData(form, requestType = 'post') {
  const values = htmx.values(form, requestType);
  
  // Add metadata
  const formData = {
    ...values,
    _timestamp: Date.now(),
    _formId: form.id,
    _action: form.action || window.location.pathname
  };
  
  // Validate required fields
  const requiredInputs = htmx.findAll(form, '[required]');
  const missingFields = Array.from(requiredInputs)
    .filter(input => !values[input.name])
    .map(input => input.name);
  
  if (missingFields.length > 0) {
    formData._errors = { missing: missingFields };
  }
  
  return formData;
}

// Dynamic form field discovery
function getFormFields(form) {
  const inputs = htmx.findAll(form, 'input:not([type="hidden"])');
  const selects = htmx.findAll(form, 'select');
  const textareas = htmx.findAll(form, 'textarea');
  
  return {
    inputs: Array.from(inputs),
    selects: Array.from(selects),
    textareas: Array.from(textareas),
    all: [...inputs, ...selects, ...textareas]
  };
}

// Smart form reset
function resetFormWithExclusions(form, excludeFields = []) {
  const fields = getFormFields(form);
  
  fields.all.forEach(field => {
    if (!excludeFields.includes(field.name)) {
      if (field.type === 'checkbox' || field.type === 'radio') {
        field.checked = false;
      } else {
        field.value = '';
      }
    }
  });
}
```

### Performance Considerations

Efficient querying patterns for better performance.

```javascript
// Cache frequently used elements
const queryCache = new Map();

function cachedFind(selector, ttl = 5000) {
  const cacheKey = selector;
  const cached = queryCache.get(cacheKey);
  
  if (cached && Date.now() - cached.timestamp < ttl) {
    return cached.element;
  }
  
  const element = htmx.find(selector);
  queryCache.set(cacheKey, {
    element: element,
    timestamp: Date.now()
  });
  
  return element;
}

// Batch operations
function batchQuery(selectors) {
  const results = {};
  selectors.forEach(selector => {
    results[selector] = htmx.findAll(selector);
  });
  return results;
}

// Usage
const elements = batchQuery([
  'button[data-action]',
  'form[data-validate]',
  '.error-message',
  '[data-tooltip]'
]);

// Scoped querying to avoid document-wide searches
function scopedOperations(containerId) {
  const container = htmx.find(`#${containerId}`);
  if (!container) return;
  
  // All subsequent queries are scoped to this container
  const buttons = htmx.findAll(container, 'button');
  const inputs = htmx.findAll(container, 'input');
  const errors = htmx.findAll(container, '.error');
  
  // Process scoped elements
  return { buttons, inputs, errors };
}
```
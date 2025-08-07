---
title: Getting Started
description: Learn how to install and use Runed in your projects.
category: Anchor
---

## Installation

Install Runed using your favorite package manager:

```bash
npm install runed
```

## Usage

Import one of the utilities you need to either a `.svelte` or `.svelte.js|ts` file and start using
it:

```svelte title="component.svelte"
<script lang="ts">
	import { activeElement } from "runed";

	let inputElement = $state<HTMLInputElement | undefined>();
</script>

<input bind:this={inputElement} />

{#if activeElement.current === inputElement}
	The input element is active!
{/if}
```

or

```ts title="some-module.svelte.ts"
import { activeElement } from "runed";

function logActiveElement() {
	$effect(() => {
		console.log("Active element is ", activeElement.current);
	});
}

logActiveElement();
```

---
title: Context
description:
  A wrapper around Svelte's Context API that provides type safety and improved ergonomics for
  sharing data between components.
category: State
---

<script>
	import { Steps, Step, Callout } from '@svecodocs/kit';
</script>

Context allows you to pass data through the component tree without explicitly passing props through
every level. It's useful for sharing data that many components need, like themes, authentication
state, or localization preferences.

The `Context` class provides a type-safe way to define, set, and retrieve context values.

## Usage

<Steps>

<Step>Creating a Context</Step>

First, create a `Context` instance with the type of value it will hold:

```ts title="context.ts"
import { Context } from "runed";

export const myTheme = new Context<"light" | "dark">("theme");
```

Creating a `Context` instance only defines the context - it doesn't actually set any value. The
value passed to the constructor (`"theme"` in this example) is just an identifier used for debugging
and error messages.

Think of this step as creating a "container" that will later hold your context value. The container
is typed (in this case to only accept `"light"` or `"dark"` as values) but remains empty until you
explicitly call `myTheme.set()` during component initialization.

This separation between defining and setting context allows you to:

- Keep context definitions in separate files
- Reuse the same context definition across different parts of your app
- Maintain type safety throughout your application
- Set different values for the same context in different component trees

<Step>Setting Context Values</Step>

Set the context value in a parent component during initialization.

```svelte title="+layout.svelte"
<script lang="ts">
	import { myTheme } from "./context";
	let { data, children } = $props();

	myTheme.set(data.theme);
</script>

{@render children?.()}
```

<Callout>

Context must be set during component initialization, similar to lifecycle functions like `onMount`.
You cannot set context inside event handlers or callbacks.

</Callout>

<Step>Reading Context Values</Step>

Child components can access the context using `get()` or `getOr()`

```svelte title="+page.svelte"
<script lang="ts">
	import { myTheme } from "./context";

	const theme = myTheme.get();
	// or with a fallback value if the context is not set
	const theme = myTheme.getOr("light");
</script>
```

</Steps>

## Type Definition

```ts
class Context<TContext> {
	/**
	 * @param name The name of the context.
	 * This is used for generating the context key and error messages.
	 */
	constructor(name: string) {}

	/**
	 * The key used to get and set the context.
	 *
	 * It is not recommended to use this value directly.
	 * Instead, use the methods provided by this class.
	 */
	get key(): symbol;

	/**
	 * Checks whether this has been set in the context of a parent component.
	 *
	 * Must be called during component initialization.
	 */
	exists(): boolean;

	/**
	 * Retrieves the context that belongs to the closest parent component.
	 *
	 * Must be called during component initialization.
	 *
	 * @throws An error if the context does not exist.
	 */
	get(): TContext;

	/**
	 * Retrieves the context that belongs to the closest parent component,
	 * or the given fallback value if the context does not exist.
	 *
	 * Must be called during component initialization.
	 */
	getOr<TFallback>(fallback: TFallback): TContext | TFallback;

	/**
	 * Associates the given value with the current component and returns it.
	 *
	 * Must be called during component initialization.
	 */
	set(context: TContext): TContext;
}
```

---
title: ScrollState
description:
  Track scroll position, direction, and edge states with support for programmatic scrolling.
category: Elements
---

<script>
import Demo from '$lib/components/demos/scroll-state.svelte';
</script>

## Demo

<Demo />

## Overview

`ScrollState` is a reactive utility that lets you:

- Track scroll positions (`x` / `y`)
- Detect scroll direction (`left`, `right`, `top`, `bottom`)
- Determine if the user has scrolled to an edge (`arrived` state)
- Perform programmatic scrolling (`scrollTo`, `scrollToTop`, `scrollToBottom`)
- Listen to scroll and scroll-end events
- Respect flex, RTL, and reverse layout modes

Inspired by [VueUse's `useScroll`](https://vueuse.org/useScroll), this utility is built for Svelte
and works with DOM elements, the `window`, or `document`.

## Usage

```svelte
<script lang="ts">
	import { ScrollState } from "runed";

	let el = $state<HTMLElement>();

	const scroll = new ScrollState({
		element: () => el
	});
</script>

<div bind:this={el} style="overflow: auto; height: 200px;">
	<!-- scrollable content here -->
</div>
```

You can now access:

- `scroll.x` and `scroll.y` — current scroll positions (reactive, get/set)

- `scroll.directions` — active scroll directions

- `scroll.arrived` — whether the scroll has reached each edge

- `scroll.progress` — percentage that the user has scrolled on the x/y axis

- `scroll.scrollTo(x, y)` — programmatic scroll

- `scroll.scrollToTop()` and `scroll.scrollToBottom()` — helpers

## Options

You can configure `ScrollState` via the following options:

| Option                 | Type                                                     | Description                                                            |
| ---------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------- |
| `element`              | `MaybeGetter<HTMLElement \| Window \| Document \| null>` | The scroll container (required).                                       |
| `idle`                 | `MaybeGetter<number \| undefined>`                       | Debounce time (ms) after scroll ends. Default: `200`.                  |
| `offset`               | `{ top?, bottom?, left?, right? }`                       | Pixel thresholds for "arrived" state detection. Default: `0` for all.  |
| `onScroll`             | `(e: Event) => void`                                     | Callback for scroll events.                                            |
| `onStop`               | `(e: Event) => void`                                     | Callback after scrolling stops.                                        |
| `eventListenerOptions` | `AddEventListenerOptions`                                | Scroll listener options. Default: `{ passive: true, capture: false }`. |
| `behavior`             | `ScrollBehavior`                                         | Scroll behavior: `"auto"`, `"smooth"`, etc. Default: `"auto"`.         |
| `onError`              | `(error: unknown) => void`                               | Optional error handler. Default: `console.error`.                      |

## Notes

- Both scroll position (`x`, `y`) and edge arrival state (`arrived`) are reactive values.

- You can programmatically change `scroll.x` and `scroll.y`, and the element will scroll
  accordingly.

- Layout direction and reverse flex settings are respected when calculating edge states.

- Debounced `onStop` is invoked after scrolling ends and the user is idle.

---
title: PressedKeys
description: Tracks which keys are currently pressed
category: Sensors
---

<script>
import Demo from '$lib/components/demos/pressed-keys.svelte';
</script>

## Demo

<Demo />

## Usage

With an instance of `PressedKeys`, you can use the `has` method.

```ts
const keys = new PressedKeys();

const isArrowDownPressed = $derived(keys.has("ArrowDown"));
const isCtrlAPressed = $derived(keys.has("Control", "a"));
```

Or get all of the currently pressed keys:

```ts
const keys = new PressedKeys();
console.log(keys.all);
```

Or register a callback to execute when specified key combination is pressed:

```ts
const keys = new PressedKeys();
keys.onKeys(["meta", "k"], () => {
	console.log("open command palette");
});
```

---
title: onClickOutside
description: Handle clicks outside of a specified element.
category: Sensors
---

<script>
import Demo from '$lib/components/demos/on-click-outside.svelte';
import DemoDialog from '$lib/components/demos/on-click-outside-dialog.svelte';
import { PropField } from '@svecodocs/kit'
</script>

`onClickOutside` detects clicks that occur outside a specified element's boundaries and executes a
callback function. It's commonly used for dismissible dropdowns, modals, and other interactive
components.

## Demo

<Demo />

## Basic Usage

```svelte
<script lang="ts">
	import { onClickOutside } from "runed";

	let container = $state<HTMLElement>()!;

	onClickOutside(
		() => container,
		() => console.log("clicked outside")
	);
</script>

<div bind:this={container}>
	<!-- Container content -->
</div>
<button>I'm outside the container</button>
```

## Advanced Usage

### Controlled Listener

The function returns control methods to programmatically manage the listener, `start` and `stop` and
a reactive read-only property `enabled` to check the current status of the listeners.

```svelte
<script lang="ts">
	import { onClickOutside } from "runed";

	let dialog = $state<HTMLDialogElement>()!;

	const clickOutside = onClickOutside(
		() => dialog,
		() => {
			dialog.close();
			clickOutside.stop();
		},
		{ immediate: false }
	);

	function openDialog() {
		dialog.showModal();
		clickOutside.start();
	}

	function closeDialog() {
		dialog.close();
		clickOutside.stop();
	}
</script>

<button onclick={openDialog}>Open Dialog</button>
<dialog bind:this={dialog}>
	<div>
		<button onclick={closeDialog}>Close Dialog</button>
	</div>
</dialog>
```

Here's an example of using `onClickOutside` with a `<dialog>`:

<DemoDialog />

## Options

<PropField name="immediate" type="boolean" defaultValue="true">

Whether the click outside handler is enabled by default or not. If set to `false`, the handler will
not be active until enabled by calling the returned `start` function.

</PropField>

<PropField name="detectIframe" type="boolean" defaultValue="false">

Controls whether focus events from iframes trigger the callback. Since iframe click events don't
bubble to the parent document, you may want to enable this if you need to detect when users interact
with iframe content.

</PropField>

<PropField name="document" type="Document" defaultValue="document">

The document object to use, defaults to the global document.

</PropField>

<PropField name="window" type="Window" defaultValue="window">

The window object to use, defaults to the global window.

</PropField>

## Type Definitions

```ts
export type OnClickOutsideOptions = ConfigurableWindow &
	ConfigurableDocument & {
		/**
		 * Whether the click outside handler is enabled by default or not.
		 * If set to false, the handler will not be active until enabled by
		 * calling the returned `start` function
		 *
		 * @default true
		 */
		immediate?: boolean;
		/**
		 * Controls whether focus events from iframes trigger the callback.
		 *
		 * Since iframe click events don't bubble to the parent document,
		 * you may want to enable this if you need to detect when users
		 * interact with iframe content.
		 *
		 * @default false
		 */
		detectIframe?: boolean;
	};
/**
 * A utility that calls a given callback when a click event occurs outside of
 * a specified container element.
 *
 * @template T - The type of the container element, defaults to HTMLElement.
 * @param {MaybeElementGetter<T>} container - The container element or a getter function that returns the container element.
 * @param {() => void} callback - The callback function to call when a click event occurs outside of the container.
 * @param {OnClickOutsideOptions} [opts={}] - Optional configuration object.
 * @param {ConfigurableDocument} [opts.document=defaultDocument] - The document object to use, defaults to the global document.
 * @param {boolean} [opts.immediate=true] - Whether the click outside handler is enabled by default or not.
 * @param {boolean} [opts.detectIframe=false] - Controls whether focus events from iframes trigger the callback.
 *
 * @see {@link https://runed.dev/docs/utilities/on-click-outside}
 */
export declare function onClickOutside<T extends Element = HTMLElement>(
	container: MaybeElementGetter<T>,
	callback: (event: PointerEvent | FocusEvent) => void,
	opts?: OnClickOutsideOptions
): {
	/** Stop listening for click events outside the container. */
	stop: () => boolean;
	/** Start listening for click events outside the container. */
	start: () => boolean;
	/** Whether the click outside handler is currently enabled or not. */
	readonly enabled: boolean;
};
```

---
title: IsInViewport
description: Track if an element is visible within the current viewport.
category: Elements
---

<script>
import Demo from '$lib/components/demos/is-in-viewport.svelte';
</script>

`IsInViewport` uses the [`useIntersectionObserver`](/docs/utilities/use-intersection-observer)
utility to track if an element is visible within the current viewport.

It accepts an element or getter that returns an element and an optional `options` object that aligns
with the [`useIntersectionObserver`](/docs/utilities/use-intersection-observer) utility options.

## Demo

<Demo />

## Usage

```svelte
<script lang="ts">
	import { IsInViewport } from "runed";

	let targetNode = $state<HTMLElement>()!;
	const inViewport = new IsInViewport(() => targetNode);
</script>

<p bind:this={targetNode}>Target node</p>

<p>Target node in viewport: {inViewport.current}</p>
```

## Type Definition

```ts
import { type UseIntersectionObserverOptions } from "runed";
export type IsInViewportOptions = UseIntersectionObserverOptions;

export declare class IsInViewport {
	constructor(node: MaybeGetter<HTMLElement | null | undefined>, options?: IsInViewportOptions);
	get current(): boolean;
}
```

<!-- Ensure the page can scroll so the target can be outside of the viewport -->
<div class="h-[500px]"></div>

---
title: PersistedState
description:
  A reactive state manager that persists and synchronizes state across browser sessions and tabs
  using Web Storage APIs.
category: State
---

<script>
import Demo from '$lib/components/demos/persisted-state.svelte';
import { Callout } from '@svecodocs/kit'
</script>

`PersistedState` provides a reactive state container that automatically persists data to browser
storage and optionally synchronizes changes across browser tabs in real-time.

## Demo

<Demo />
<Callout>
	You can refresh this page and/or open it in another tab to see the count state being persisted
	and synchronized across sessions and tabs.
</Callout>

## Usage

Initialize `PersistedState` by providing a unique key and an initial value for the state.

```svelte
<script lang="ts">
	import { PersistedState } from "runed";

	const count = new PersistedState("count", 0);
</script>

<div>
	<button onclick={() => count.current++}>Increment</button>
	<button onclick={() => count.current--}>Decrement</button>
	<button onclick={() => (count.current = 0)}>Reset</button>
	<p>Count: {count.current}</p>
</div>
```

### Complex objects

When persisting complex objects, only plain structures are deeply reactive.

This includes arrays, plain objects, and primitive values.

For example:

```ts
const persistedArray = new PersistedState("foo", ["a", "b"]);
persistedArray.current.push("c"); // This will persist the change

const persistedObject = new PersistedState("bar", { name: "Bob" });
persistedObject.current.name = "JG"; // This will persist the change

class Person {
	name: string;
	constructor(name: string) {
		this.name = name;
	}
}
const persistedComplexObject = new PersistedState("baz", new Person("Bob"));
persistedComplexObject.current.name = "JG"; // This will NOT persist the change
persistedComplexObject.current = new Person("JG"); // This will persist the change
```

## Configuration Options

`PersistedState` includes an `options` object that allows you to customize the behavior of the state
manager.

```ts
const state = new PersistedState("user-preferences", initialValue, {
	// Use sessionStorage instead of localStorage (default: 'local')
	storage: "session",

	// Disable cross-tab synchronization (default: true)
	syncTabs: false,

	// Custom serialization handlers
	serializer: {
		serialize: superjson.stringify,
		deserialize: superjson.parse
	}
});
```

### Storage Options

- `'local'`: Data persists until explicitly cleared
- `'session'`: Data persists until the browser session ends

### Cross-Tab Synchronization

When `syncTabs` is enabled (default), changes are automatically synchronized across all browser tabs
using the storage event.

### Custom Serialization

Provide custom `serialize` and `deserialize` functions to handle complex data types:

```ts
import superjson from "superjson";

// Example with Date objects
const lastAccessed = new PersistedState("last-accessed", new Date(), {
	serializer: {
		serialize: superjson.stringify,
		deserialize: superjson.parse
	}
});
```



---
title: FiniteStateMachine
description: Defines a strongly-typed finite state machine.
category: State
---

<script>
	import Demo from '$lib/components/demos/finite-state-machine.svelte';
</script>

## Demo

<Demo />

```ts
type MyStates = "disabled" | "idle" | "running";
type MyEvents = "toggleEnabled" | "start" | "stop";
const f = new FiniteStateMachine<MyStates, MyEvents>("disabled", {
	disabled: {
		toggleEnabled: "idle"
	},
	idle: {
		toggleEnabled: "disabled",
		start: "running"
	},
	running: {
		_enter: () => {
			f.debounce(2000, "stop");
		},
		stop: "idle",
		toggleEnabled: "disabled"
	}
});
```

## Usage

Finite state machines (often abbreviated as "FSMs") are useful for tracking and manipulating
something that could be in one of many different states. It centralizes the definition of every
possible _state_ and the _events_ that might trigger a transition from one state to another. Here is
a state machine describing a simple toggle switch:

```ts
import { FiniteStateMachine } from "runed";
type MyStates = "on" | "off";
type MyEvents = "toggle";

const f = new FiniteStateMachine<MyStates, MyEvents>("off", {
	off: {
		toggle: "on"
	},
	on: {
		toggle: "off"
	}
});
```

The first argument to the `FiniteStateMachine` constructor is the initial state. The second argument
is an object with one key for each state. Each state then describes which events are valid for that
state, and which state that event should lead to.

In the above example of a simple switch, there are two states (`on` and `off`). The `toggle` event
in either state leads to the other state.

You send events to the FSM using `f.send`. To send the `toggle` event, invoke `f.send('toggle')`.

### Actions

Maybe you want fancier logic for an event handler, or you want to conditionally transition into
another state. Instead of strings, you can use _actions_.

An action is a function that returns a state. An action can receive parameters, and it can use those
parameters to dynamically choose which state should come next. It can also prevent a state
transition by returning nothing.

```ts
type MyStates = "on" | "off" | "cooldown";

const f = new FiniteStateMachine<MyStates, MyEvents>("off", {
	off: {
		toggle: () => {
			if (isTuesday) {
				// Switch can only turn on during Tuesdays
				return "on";
			}
			// All other days, nothing is returned and state is unchanged.
		}
	},
	on: {
		toggle: (heldMillis: number) => {
			// You can also dynamically return the next state!
			// Only turn off if switch is depressed for 3 seconds
			if (heldMillis > 3000) {
				return "off";
			}
		}
	}
});
```

### Lifecycle methods

You can define special handlers that are invoked whenever a state is entered or exited:

```ts
const f = new FiniteStateMachine<MyStates, MyEvents>('off', {
	off: {
		toggle: 'on'
		_enter: (meta) => { console.log('switch is off') }
		_exit: (meta) => { console.log('switch is no longer off') }
	},
	on: {
		toggle: 'off'
		_enter: (meta) => { console.log('switch is on') }
		_exit: (meta) => { console.log('switch is no longer on') }
	}
});
```

The lifecycle methods are invoked with a metadata object containing some useful information:

- `from`: the name of the event that is being exited
- `to`: the name of the event that is being entered
- `event`: the name of the event which has triggered the transition
- `args`: (optional) you may pass additional metadata when invoking an action with
  `f.send('theAction', additional, params, as, args)`

The `_enter` handler for the initial state is called upon creation of the FSM. It is invoked with
both the `from` and `event` fields set to `null`.

### Wildcard handlers

There is one special state used as a fallback: `*`. If you have the fallback state, and you attempt
to `send()` an event that is not handled by the current state, then it will try to find a handler
for that event on the `*` state before discarding the event:

```ts
const f = new FiniteStateMachine<MyStates, MyEvents>('off', {
	off: {
		toggle: 'on'
	},
	on: {
		toggle: 'off'
	}
	'*': {
		emergency: 'off'
	}
});

// will always result in the switch turning off.
f.send('emergency');
```

### Debouncing

Frequently, you want to transition to another state after some time has elapsed. To do this, use the
`debounce` method:

```ts
f.send("toggle"); // turn on immediately
f.debounce(5000, "toggle"); // turn off in 5000 milliseconds
```

If you re-invoke debounce with the same event, it will cancel the existing timer and start the
countdown over:

```ts
// schedule a toggle in five seconds
f.debounce(5000, "toggle");
// ... less than 5000ms elapses ...
f.debounce(5000, "toggle");
// The second call cancels the original timer, and starts a new one
```

You can also use `debounce` in both actions and lifecycle methods. In both of the following
examples, the lightswitch will turn itself off five seconds after it was turned on:

```ts
const f = new FiniteStateMachine<MyStates, MyEvents>("off", {
	off: {
		toggle: () => {
			f.debounce(5000, "toggle");
			return "on";
		}
	},
	on: {
		toggle: "off"
	}
});
```

```ts
const f = new FiniteStateMachine<MyStates, MyEvents>("off", {
	off: {
		toggle: "on"
	},
	on: {
		toggle: "off",
		_enter: () => {
			f.debounce(5000, "toggle");
		}
	}
});
```

## Notes

`FiniteStateMachine` is a loving rewrite of
[kenkunz/svelte-fsm](https://github.com/kenkunz/svelte-fsm).

FSMs are ideal for representing many different kinds of systems and interaction patterns.
`FiniteStateMachine` is an intentionally minimalistic implementation. If you're looking for a more
powerful FSM library, [statelyai/xstate](https://github.com/statelyai/xstate) is an excellent
library with more features&thinsp;—&thinsp;and a steeper learning curve.---
title: ElementSize
description: Track element dimensions reactively
category: Elements
---

<script>
	import Demo from '$lib/components/demos/element-size.svelte';
</script>

`ElementSize` provides reactive access to an element's width and height, automatically updating when
the element's dimensions change. Similar to `ElementRect` but focused only on size measurements.

## Demo

<Demo />

## Usage

```svelte
<script lang="ts">
	import { ElementSize } from "runed";

	let el = $state() as HTMLElement;
	const size = new ElementSize(() => el);
</script>

<textarea bind:this={el}></textarea>

<p>Width: {size.width} Height: {size.height}</p>
```

## Type Definition

```ts
interface ElementSize {
	readonly width: number;
	readonly height: number;
}
```
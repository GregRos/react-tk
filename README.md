# reactk

Reactk is an experimental framework building Tkinter UIs using React principles.

## Step by step

### Importing

First, let's import the stuff we'll need:

```python
from reactk import Window, WindowRoot, Widget, Label, Component
```

1. The `WindowRoot` which is used to mount components into Tk.
2. The `Window` node that represents a window.
3. The `Label` node that represents a Label.
4. The `Component` base class.
5. The `Widget` node we use to express Widget components.

### Define a custom widget component

We typically define Components as dataclasses with `kw_only=True`. This Component should have a `render` method that returns other components or ShadowNode objects, such as those representing various Tk elements.

In this case, our component returns a single `Label`.

The Label's props are divided into the base props and the layout manager props. To set to layout manager props, you need to call the appropriate method on the Widget ShadowNode.

Right now only `Pack` is supported.

```python
Label().Pack(
    ipadx=20,
    fill="both"
)
```

Return this from your component:

```python
@dataclass(kw_only=True)
class TextComponent(Component[Widget]):
    text: str

    def render(self):
        return Label(
            text=self.text,
            background="#000001",
            foreground="#ffffff",
            font=Font(family="Arial", size=20, style="bold"),
        ).Pack(ipadx=20, ipady=15, fill="both")
```

### Define a custom Window component

Widgets are must be contained in Windows. Windows aren't contained in anything, as we'll see. We need to create a component that returns Window nodes.

To have our previous component be contained in a Window node, we create the Window node and then use `[...]` square brackets to specify children.

```py
Window()[
    TextComponent(text="abc")
]
```

Now we create the Window component. We'll use context, which works kind of like in React. It's passed down all the components. You can access it from a component using `self.ctx`.

```py
@dataclass(kw_only=True)
class WindowComponent(Component[Window]):
    def render(self):
        displayed_text = self.ctx.text
        lbl = Label(
            text=displayed_text,
            background="#000001",
            foreground="#ffffff",
            font=Font(family="Arial", size=20, style="bold"),
        ).Pack(ipadx=20, ipady=15, fill="both")
        return Window(topmost=True, background="black", alpha=85).Geometry(
            width=500, height=500, x=500, y=500, anchor_point="lt"
        )[lbl]
```

1. Inherent Window props are set via the constructor.
2. Window Geometry is kind of like a layout manager and is set separately.

#### Using a single component

You can also just use a single Window component. you don't have to use a widget component at all.

```py
@dataclass(kw_only=True)
class WindowComponent(Component[Window]):

    def render(self):
        lbl = Label(
            text=self.ctx.text,
            background="#000001",
            foreground="#ffffff",
            font=Font(family="Arial", size=20, style="bold"),
        ).Pack(ipadx=20, ipady=15, fill="both")
        return Window(topmost=True, background="black", alpha=85).Geometry(
            width=500, height=500, x=500, y=500, anchor_point="lt"
        )[lbl]
```

### Create a WindowRoot

Windows aren't contained in anything. Instead they're "mounted" on the WindowRoot. To do that, we create a `WindowRoot` around a specific component instance. We can pass it kwargs to initialize its context.

Once the WindowRoot is constructed, the UI will immediately mount. However, the context starts out as an empty object.

To add attributes to it, we can pass them as kwargs to the `WindowRoot` constructor:

```py
ui_root = WindowRoot(WindowComponent(), text="Hello World!")
```

After this, we can modify the context any time by "calling" the `WindowRoot` with kwargs, like this:

```py
ui_root(text="Hello again!")
```

This will regenerate the component tree and reconcile any changes with the mounted UI.

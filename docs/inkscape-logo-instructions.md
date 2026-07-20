# Libby Church Logo — Inkscape Editing Instructions

Reference image: the white-background PNG export from GIMP (mountains + waves, no dove).

---

## Setup

1. Download and install Inkscape from **inkscape.org** (free)
2. Open Inkscape
3. File → **Import** → select the white-background PNG → click **OK**
4. The image appears on the canvas. Click it once to select it.
5. Object → **Objects** panel (if not visible: Object → Objects...)
6. In the Objects panel, double-click the layer name → rename it **"reference"**
7. Click the **lock icon** next to "reference" to lock it (prevents accidental moves)
8. Layer → **Add Layer** → name it **"mountains"** → click Add

---

## Understanding your mountain shape

Your mountains are drawn as **two separate thick lines** (like marker strokes with rounded ends):

- **Line 1 — outer ridge**: The large left peak. Starts bottom-left, angles up to the main peak, comes back down, and forms the base.
- **Line 2 — inner ridge**: The smaller peaks to the right. Overlaps with Line 1, creating the layered depth.
- Both lines use **thick rounded strokes** (rounded ends and corners).

The two problems to fix:
- **Base angle**: There is a slight horizontal section at the bottom-left before the line starts going up. It should angle immediately.
- **Parallel gap**: The gap between the outer and inner lines widens slightly toward the ends. It should stay consistent.

---

## Redrawing the mountains (recommended approach)

Rather than editing the traced bitmap (which produces messy paths), redraw the mountain lines on top of the reference image. This gives you clean, editable paths.

### Step 1 — Trace the outer mountain line

1. Make sure you are on the **"mountains"** layer (click it in the Objects panel)
2. Select the **Bezier/Pen tool** (keyboard shortcut: **B**)
3. In the top toolbar, select **"Create regular Bezier path"** (the straight-line mode)
4. **Click** (do not drag) at each corner point of the outer mountain line:
   - Click at the **bottom-left base** of the mountain
   - Click at the **peak** (top of the large left triangle)
   - Click at the **valley** between peaks
   - Click at the **second peak**
   - Continue clicking at each direction-change point
   - Click at the **bottom-right base**
5. Press **Enter** to finish the path

**Base angle fix:** For your first two clicks (bottom-left → first peak), place them so the line goes immediately upward at an angle — no horizontal section in between. The Nuxt logo style: the path angles upward from the very first point.

### Step 2 — Style the outer line to match original

1. With the path selected, open **Object → Fill and Stroke** (Shift+Ctrl+F)
2. Click the **Fill** tab → click the **X** (no fill)
3. Click the **Stroke paint** tab → click the **flat color square** → set to black (R:0 G:0 B:0)
4. Click the **Stroke style** tab:
   - Width: start with **30px** and adjust to match the original thickness
   - Cap: click the **Round cap** button (middle button)
   - Join: click the **Round join** button (middle button)

### Step 3 — Create the inner parallel line

This is the key fix for the parallel gap problem.

1. With the outer line selected, press **Ctrl+D** to duplicate it
2. The duplicate sits exactly on top — it is already selected
3. Open the **XML editor** (Ctrl+Shift+X) — but actually the easier way:
4. Select the **Node tool** (keyboard shortcut: **N**)
5. Click on the duplicate path
6. Select **all nodes** (Ctrl+A)
7. Now adjust each node inward so the line is consistently inside the outer line

**Easier parallel method:**
1. Select the outer line
2. Press Ctrl+D to duplicate
3. With the duplicate selected, go to **Path → Offset** — this may not work on open paths
4. **Alternative**: Use the Transform dialog (Object → Transform → Scale tab) → scale to about 85% → check "Apply to each object separately" → uncheck "Scale stroke width" → Apply
5. Then use the **Arrow tool** to nudge the scaled copy into position over the inner mountain line in your reference image

### Step 4 — Adjust until parallel

The gap between your two lines should be the same width all the way across — at the base, up the slopes, at the peak. Use the Node tool (N) to drag individual points until the spacing looks even.

---

## Checking your work

- Temporarily hide the "reference" layer (click its eye icon in Objects panel)
- Your redrawn lines should look like the original but with:
  - Consistent gap between the two lines
  - Line angles immediately from the base point (no horizontal stub)
  - Smooth, consistent line weight throughout

---

## Saving for handoff

When you are happy with the mountain lines (waves and dove will be added later):

1. File → **Save As**
2. Change the file type to **Plain SVG** (not "Inkscape SVG")
3. Name it `libby-mountains-v2.svg`
4. Save it to your project folder

Share that SVG file here and the next steps (dove, flame trails, color variants, text layouts) can be done in code.

---

## Notes

- The **waves** do not need editing — they look great. Leave them in place on the reference layer and they will be redrawn faithfully in the final SVG.
- The **dove** will be added as a separate element above the mountains — you do not need to worry about that in Inkscape.
- If a line looks wrong, select it with the Arrow tool and press **Delete** to remove it and start that line over. Redrawing is faster than fixing bad nodes.
- **Undo** is Ctrl+Z — use it freely.

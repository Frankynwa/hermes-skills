---
name: c-code-review
description: "C language code review for embedded projects — memory safety, pointer correctness, buffer overflow detection, and LVGL best practices"
triggers:
  - user asks to review C code
  - user pastes C code for review
  - user mentions C pointer or memory issues
  - pull request with .c/.h files
autorun: false
---

# C Code Review for Embedded Projects

Specialized code review for embedded C, focused on the UT285E LVGL UI project.

## Review Checklist

### 1. Memory Safety

```c
// ❌ BAD: No bounds check
void process_data(int *buf, int len) {
    for (int i = 0; i <= len; i++)  // off-by-one!
        buf[i] = transform(buf[i]);
}

// ✅ GOOD: Bounds check + const for read-only
void process_data(int *buf, size_t len) {
    for (size_t i = 0; i < len; i++)
        buf[i] = transform(buf[i]);
}
```

**Check for:**
- [ ] Array bounds checked before access
- [ ] Null pointers checked before dereference
- [ ] `malloc`/`realloc` return values checked
- [ ] `free` called exactly once, no use-after-free
- [ ] No buffer overflow in string operations

### 2. LVGL Patterns

```c
// ❌ BAD: Object not checked
lv_obj_t *label = lv_label_create(parent);
lv_label_set_text(label, "Hello");  // label could be NULL

// ✅ GOOD: Assert or check
lv_obj_t *label = lv_label_create(parent);
LV_ASSERT_MALLOC(label);
if (label) lv_label_set_text(label, "Hello");
```

**Check for:**
- [ ] `lv_*_create()` return values checked
- [ ] Objects deleted properly with `lv_obj_del()`
- [ ] Screen lifecycle handled (active screen vs. all screens)
- [ ] Event callbacks use `lv_event_get_user_data()` correctly
- [ ] Styles applied before object becomes visible

### 3. Windows/MSVC Specific

```c
// ❌ BAD: POSIX-only
#include <unistd.h>
usleep(1000);

// ✅ GOOD: Cross-platform
#ifdef _WIN32
    #include <windows.h>
    Sleep(1);
#else
    #include <unistd.h>
    usleep(1000);
#endif
```

**Check for:**
- [ ] No `unistd.h`, `sys/ioctl.h` in Windows builds
- [ ] `SDL_main.h` included and `SDL_MAIN_HANDLED` defined
- [ ] UTF-8 BOM on source files for MSVC
- [ ] `_CRT_SECURE_NO_WARNINGS` for MSVC
- [ ] `M_PI` requires `_USE_MATH_DEFINES`

### 4. Embedded Best Practices

```c
// ❌ BAD: Stack-heavy
void draw_page(void) {
    char buf[4096];  // 4KB on stack!
}

// ✅ GOOD: Static allocation
static char draw_buf[4096];  // .bss section
void draw_page(void) { /* use draw_buf */ }
```

**Check for:**
- [ ] Large stack allocations (use static or heap)
- [ ] `volatile` for hardware registers and ISR-shared variables
- [ ] Bit manipulation uses unsigned types
- [ ] No floating point in ISR context (unless FPU context saved)
- [ ] `const` correctness for read-only data

### 5. Naming Conventions

```c
// ❌ BAD: Inconsistent naming
void CreateConfigPage(void);    // PascalCase
void draw_main_screen();        // snake_case
extern int pageMode;            // camelCase?

// ✅ GOOD: Consistent (UT285E style)
void page_config_create(lv_obj_t *parent);
void ui_sidebar_set_page(int page_id);
```

## Review Output Format

```
## C Code Review — <file/PR>

### 🔴 Critical (must fix)
- **<file>:<line>** — <issue>. Suggestion: <fix>.

### ⚠️ Warnings (should fix)
- **<file>:<line>** — <issue>.

### 💡 Suggestions
- **<file>:<line>** — <suggestion>.

### ✅ Looks Good
- <positive observation>
```

## Verified UT285E Bug Patterns

cppcheck v2.21 found on hand-written project (16 files):

**Real Bugs:**
1. `ui_page_config.c:592` — `lv_obj_t *btn` assigned but never used
2. `ui_page_simple_measure.c:246` — `info_y += 36` result discarded

**Recurring:**
- 14 non-const event targets across 5 files
- 8 mutable static arrays (should be `static const`)
- 1 redundant condition (ui_sidebar.c:44)

GUI Guider project: 0 bugs (auto-generated code is cleaner).

**GUI Guider Click**: `lv_obj_remove_flag(obj, LV_OBJ_FLAG_CLICKABLE)` on 4 imgbtns — replace with `add_flag`.

## Quick Scan Commands

```bash
# Check for common issues
grep -n "malloc\|free\|strcpy\|sprintf\|gets" src/*.c
grep -n "LV_ASSERT\|lv_obj_del\|lv_mem" src/*.c
grep -n "#include <unistd\|#include <sys/" src/*.c
```
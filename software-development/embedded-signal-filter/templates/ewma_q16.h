/**
 * @file    ewma_q16.h
 * @brief   EWMA Q16 fixed-point filter — deviation-domain, MCU-ready
 *
 * Usage:
 *   ewma_filter_t f;
 *   ewma_init(&f, 6554, 8484000);  // alpha=0.1, baseline
 *   while(1) {
 *       int32_t raw = read_adc();
 *       int32_t filtered = ewma_update(&f, raw);
 *   }
 *
 * RAM: 12 bytes per channel. CPU: ~30 cycles on Cortex-M3 @72MHz.
 */

#ifndef EWMA_Q16_H
#define EWMA_Q16_H

#include <stdint.h>

#ifndef EWMA_Q_BITS
#define EWMA_Q_BITS     16
#endif
#define EWMA_ONE_Q16    (1L << EWMA_Q_BITS)

typedef struct {
    int32_t  y_q16;       /* current output in Q16 deviation domain */
    int32_t  alpha_q16;   /* smoothing factor in Q16 */
    int32_t  baseline;    /* DC offset (target level) */
} ewma_filter_t;

static inline void ewma_init(ewma_filter_t *f, int32_t alpha_q16, int32_t baseline)
{
    f->y_q16     = 0;
    f->alpha_q16 = alpha_q16;
    f->baseline  = baseline;
}

static inline int32_t ewma_update(ewma_filter_t *f, int32_t x_raw)
{
    int32_t dev = x_raw - f->baseline;
    int64_t dev_q16 = (int64_t)dev << EWMA_Q_BITS;
    int64_t inv = EWMA_ONE_Q16 - f->alpha_q16;

    f->y_q16 = (int32_t)(
        ((int64_t)f->alpha_q16 * dev_q16 + inv * (int64_t)f->y_q16)
        >> EWMA_Q_BITS
    );

    return (f->y_q16 >> EWMA_Q_BITS) + f->baseline;
}

static inline int32_t ewma_get(const ewma_filter_t *f)
{
    return (f->y_q16 >> EWMA_Q_BITS) + f->baseline;
}

static inline void ewma_reset(ewma_filter_t *f)
{
    f->y_q16 = 0;
}

static inline void ewma_set_alpha(ewma_filter_t *f, int32_t alpha_q16)
{
    if (alpha_q16 < 1) alpha_q16 = 1;
    if (alpha_q16 > EWMA_ONE_Q16 - 1) alpha_q16 = EWMA_ONE_Q16 - 1;
    f->alpha_q16 = alpha_q16;
}

/* NOTE: ewma_set_baseline must cast to int64 before shifting to prevent overflow */
static inline void ewma_set_baseline(ewma_filter_t *f, int32_t new_baseline)
{
    int32_t shift = f->baseline - new_baseline;
    f->y_q16 += (int32_t)((int64_t)shift << EWMA_Q_BITS);  /* int64 prevents overflow */
    f->baseline = new_baseline;
}

#endif /* EWMA_Q16_H */

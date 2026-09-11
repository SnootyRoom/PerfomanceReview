<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    candles: { label: string; open: number; close: number; breakdown: string }[]
    height?: number
  }>(),
  { height: 140 },
)

const padding = 14
const barWidth = 18
const gap = 6
const slot = barWidth + gap

// Ширина считается от числа свечей, а не растягивается на всю карточку —
// иначе при малом числе событий между столбиками были бы пустоты.
const width = computed(() => Math.max(padding * 2 + barWidth, padding * 2 + props.candles.length * slot - gap))

const domain = computed(() => {
  const values = props.candles.flatMap((c) => [c.open, c.close])
  const min = Math.min(0, ...values)
  const max = Math.max(0, ...values)
  return max === min ? { min: min - 1, max: max + 1 } : { min, max }
})

const plotHeight = computed(() => props.height - padding * 2)

function valueToY(value: number) {
  const { min, max } = domain.value
  return padding + ((max - value) / (max - min)) * plotHeight.value
}

const zeroY = computed(() => valueToY(0))

const bars = computed(() =>
  props.candles.map((c, i) => {
    const x = padding + slot * i
    const yOpen = valueToY(c.open)
    const yClose = valueToY(c.close)
    const y = Math.min(yOpen, yClose)
    const h = Math.max(2, Math.abs(yOpen - yClose))
    const good = c.close >= c.open
    return { x, y, width: barWidth, height: h, good, ...c }
  }),
)
</script>

<template>
  <div v-if="candles.length" class="candles-scroll">
    <svg :width="width" :height="height" :viewBox="`0 0 ${width} ${height}`" class="candles" role="img" aria-label="Динамика по встречам">
      <line :x1="padding" :x2="width - padding" :y1="zeroY" :y2="zeroY" class="candles__zero" />
      <g v-for="(b, i) in bars" :key="i">
        <rect :x="b.x" :y="b.y" :width="b.width" :height="b.height" :fill="b.good ? 'var(--color-success)' : 'var(--color-danger)'" rx="2" />
        <title>{{ b.label }}{{ b.breakdown ? ': ' + b.breakdown : ' — без изменений' }}</title>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.candles-scroll {
  overflow-x: auto;
}
.candles {
  display: block;
}
.candles__zero {
  stroke: var(--color-border);
  stroke-width: 1;
}
</style>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    value: number // 0..100
    size?: number
    stroke?: number
    color?: string
    trackColor?: string
  }>(),
  { size: 96, stroke: 10, color: 'var(--color-primary)', trackColor: 'var(--color-surface-alt)' },
)

const radius = computed(() => (props.size - props.stroke) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const offset = computed(() => circumference.value * (1 - Math.max(0, Math.min(100, props.value)) / 100))
</script>

<template>
  <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`" role="img" :aria-label="`${value}%`">
    <circle :cx="size / 2" :cy="size / 2" :r="radius" fill="none" :stroke="trackColor" :stroke-width="stroke" />
    <circle
      :cx="size / 2"
      :cy="size / 2"
      :r="radius"
      fill="none"
      :stroke="color"
      :stroke-width="stroke"
      stroke-linecap="round"
      :stroke-dasharray="circumference"
      :stroke-dashoffset="offset"
      :transform="`rotate(-90 ${size / 2} ${size / 2})`"
      style="transition: stroke-dashoffset 0.4s ease"
    />
    <text
      :x="size / 2"
      :y="size / 2"
      text-anchor="middle"
      dominant-baseline="central"
      :font-size="size * 0.22"
      font-weight="800"
      fill="var(--color-text)"
    >
      {{ Math.round(value) }}%
    </text>
  </svg>
</template>

import type { Component } from 'vue'
import type { Meeting, PlanItem } from '@/types'
import { Award, Flame, Rocket, Sparkles, Star, Trophy } from '@lucide/vue'

export interface Achievement {
  id: string
  label: string
  description: string
  icon: Component
  earned: boolean
}

// Badges are pure derived data, computed from plan/meeting history — nothing stored or seeded.
export function computeAchievements(planItems: PlanItem[], meetings: Meeting[]): Achievement[] {
  const confirmed = planItems.filter((p) => p.status === 'confirmed').length
  const hasProblems = planItems.some((p) => p.status === 'problem')
  const completionRate = planItems.length ? confirmed / planItems.length : 0

  return [
    {
      id: 'first-skill',
      label: 'Первые шаги',
      description: 'Подтверждён первый навык',
      icon: Sparkles,
      earned: confirmed >= 1,
    },
    {
      id: 'five-skills',
      label: 'Растущий профессионал',
      description: 'Подтверждено 5 навыков',
      icon: Star,
      earned: confirmed >= 5,
    },
    {
      id: 'ten-skills',
      label: 'Эксперт',
      description: 'Подтверждено 10 навыков',
      icon: Trophy,
      earned: confirmed >= 10,
    },
    {
      id: 'clean-plan',
      label: 'Без просрочек',
      description: 'В плане нет ни одного просроченного навыка',
      icon: Flame,
      earned: planItems.length > 0 && !hasProblems,
    },
    {
      id: 'full-plan',
      label: 'План выполнен',
      description: 'Все навыки годового плана подтверждены',
      icon: Award,
      earned: planItems.length >= 3 && completionRate === 1,
    },
    {
      id: 'active-growth',
      label: 'Активный рост',
      description: 'Проведено 3+ PR-встречи',
      icon: Rocket,
      earned: meetings.length >= 3,
    },
  ]
}

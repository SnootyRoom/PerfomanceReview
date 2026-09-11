<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import BaseCard from '@/components/ui/BaseCard.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { MessageCircle } from '@lucide/vue'

const auth = useAuthStore()
const toast = useToast()

const vkUserId = ref(auth.currentUser?.vkUserId ?? '')
const saving = ref(false)
const testing = ref(false)

async function save() {
  saving.value = true
  try {
    await auth.updateMyNotifications(vkUserId.value.trim() || null)
    toast.success('Настройки уведомлений сохранены')
  } catch (e) {
    toast.error(e instanceof Error ? e.message : 'Не удалось сохранить')
  } finally {
    saving.value = false
  }
}

async function sendTest() {
  testing.value = true
  try {
    await auth.sendTestNotification()
    toast.success('Тестовое сообщение отправлено ВКонтакте')
  } catch (e) {
    toast.error(e instanceof Error ? e.message : 'Не удалось отправить сообщение')
  } finally {
    testing.value = false
  }
}
</script>

<template>
  <BaseCard>
    <div class="row gap-sm" style="margin-bottom: 10px">
      <MessageCircle :size="18" class="text-muted" />
      <p style="font-weight: 700">Уведомления ВКонтакте</p>
    </div>
    <p class="text-sm text-muted" style="margin-bottom: 12px">
      Укажите свой ID пользователя VK — напомним о приближающихся плановых датах подтверждения навыков и пришлём
      уведомление после каждой PR-встречи. Чтобы сообщения доходили, один раз напишите что-нибудь сообществу бота
      ВКонтакте — так VK разрешит ему писать вам первым.
    </p>
    <div class="row gap-sm wrap">
      <div style="flex: 1; min-width: 160px">
        <BaseInput v-model="vkUserId" placeholder="ID пользователя VK" />
      </div>
      <BaseButton size="sm" variant="secondary" :loading="saving" @click="save">Сохранить</BaseButton>
      <BaseButton size="sm" variant="ghost" :loading="testing" :disabled="!auth.currentUser?.vkUserId" @click="sendTest">
        Тест
      </BaseButton>
    </div>
  </BaseCard>
</template>

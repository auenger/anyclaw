export type ChatItem = {
  chat_id: string  // 完整 session key，如 "api:conv_1711084800"
  conversation_id: string  // 短 ID，如 "conv_1711084800"
  name: string
  agent_id: string
  channel: string
  last_message_time: string
  last_message: string | null
  avatar: string | null
  message_count: number
  created_at: string | null
}

// Import preset avatar images
import img01 from '../../headimg/01.jpg'
import img02 from '../../headimg/02.jpg'
import img03 from '../../headimg/03.jpg'
import img04 from '../../headimg/04.jpg'
import img05 from '../../headimg/05.jpg'
import img06 from '../../headimg/06.jpg'
import img07 from '../../headimg/07.jpg'
import img08 from '../../headimg/08.jpg'

/** 8 preset avatar images */
export const PRESET_AVATARS = [img01, img02, img03, img04, img05, img06, img07, img08] as const

/** Resolve avatar field to image URL */
export function resolveAvatar(avatar: string | null): string | null {
  if (!avatar) return null
  if (avatar.startsWith('avatar:')) {
    const index = parseInt(avatar.split(':')[1], 10)
    return PRESET_AVATARS[index] ?? PRESET_AVATARS[0]
  }
  // Backward compatibility: gradient type returns null (use default bee)
  if (avatar.startsWith('gradient:')) {
    return null
  }
  return null
}

// Group chats by date
export function groupChatsByDate(
  chats: ChatItem[],
  labels: { today: string; yesterday: string; older: string }
): { label: string; items: ChatItem[] }[] {
  const now = new Date()
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const yesterdayStart = todayStart - 86_400_000

  const today: ChatItem[] = []
  const yesterday: ChatItem[] = []
  const older: ChatItem[] = []

  for (const chat of chats) {
    const time = new Date(chat.last_message_time).getTime()
    if (time >= todayStart) today.push(chat)
    else if (time >= yesterdayStart) yesterday.push(chat)
    else older.push(chat)
  }

  const groups: { label: string; items: ChatItem[] }[] = []
  if (today.length) groups.push({ label: labels.today, items: today })
  if (yesterday.length) groups.push({ label: labels.yesterday, items: yesterday })
  if (older.length) groups.push({ label: labels.older, items: older })
  return groups
}

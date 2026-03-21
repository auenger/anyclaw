import type { en } from './en'

// 递归将所有字面量字符串宽化为 string，保留结构
type DeepStringify<T> = T extends string
  ? string
  : T extends object
    ? { readonly [K in keyof T]: DeepStringify<T[K]> }
    : T

export type Translations = DeepStringify<typeof en>

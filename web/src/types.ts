export type Type = 'N' | 'W' | 'R' | 'I'

export interface Tag {
  k: string
  v: string
  key: string
  value: string
}

export interface Elem {
  type: Type
  id: string
  version: number
  tags: Tag[]
}

export interface Fix {
  type: string
  id: string
  create: { [key: string]: string }
  modify: { [key: string]: string }
  delete: string[]
}

export interface ItemState {
  item?: string
  level?: string
  tags?: string[]
  fixable?: string[]
  class?: number
  useDevItem?: string
  source?: number
  username?: string
  country?: string
  issue_uuid?: string
}

export interface LanguagesName {
  [lang: string]: {
    name: string
    direction?: string
  }
}

export type Levels = ('1' | '2' | '3')[]

export interface Item {
  class_format: string
  item: number
  class: { class: string; title: { auto: string } }[]
  item_format: string
  levels_format: Object
  levels: { level: number; count: number }[]
  selected: boolean
  tags: string[]
}

export interface Category {
  id: number
  items: Item[]
}

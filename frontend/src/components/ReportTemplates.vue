<template>
  <component :is="templateComponent" :theme="theme" />
</template>

<script setup lang="ts">
import { computed, defineComponent, h } from 'vue'

interface TemplateProps {
  theme: {
    primaryColor: string
    secondaryColor: string
    headerBg: string
    tableBorder: string
    headerTextColor: string
    sectionBg: string
    gradient: string
  }
  layout: 'table' | 'timeline' | 'cards' | 'matrix' | 'list' | 'circles'
}

const props = defineProps<TemplateProps>()

const reportData = [
  { category: '기후변화 대응', topic: '기후변화 대응 체계', impact: '기후변화 취약성 평가 및 관리 방안 구축', stakeholder: '국내외 기후변화 관련 규제 모니터링...' },
  { category: '순환경제', topic: '자원 사용량 및 폐기물 배출', impact: '자원 사용량 및 폐기물 배출량 모니터링', stakeholder: '제품의 수명주기별 환경영향 최소화...' },
  { category: '', topic: '플라스틱 사용량', impact: '플라스틱 사용량 모니터링', stakeholder: '플라스틱 사용량 관리 및 재활용률 제고...' },
  { category: '생물다양성', topic: '생물다양성 관리 체계', impact: '생물다양성 취약지역 모니터링', stakeholder: '해양 보호지역 및 생태계 영향 최소화...' },
  { category: '공급망 ESG관리', topic: '공급망 ESG 실사', impact: 'ESG 리스크 평가 및 관리체계 운영', stakeholder: '공급망 ESG 리스크 파악 및 개선...' }
]

const templateComponent = computed(() => {
  switch (props.layout) {
    case 'table':
      return defineComponent({
        props: ['theme'],
        render() {
          return h('div', {
            style: {
              background: '#FFFFFF',
              border: `1px solid ${this.theme.tableBorder}`,
              borderRadius: '12px',
              overflow: 'hidden'
            }
          }, [
            h('table', { style: { width: '100%', borderCollapse: 'collapse' } }, [
              h('thead', [
                h('tr', { style: { background: this.theme.headerBg } }, [
                  ['구분', '토픽', '영향평가', '이해관계자 요구'].map(text =>
                    h('th', {
                      style: {
                        padding: '14px 16px',
                        textAlign: 'left',
                        fontSize: '12px',
                        fontWeight: 600,
                        color: this.theme.headerTextColor,
                        borderBottom: `1px solid ${this.theme.tableBorder}`
                      }
                    }, text)
                  )
                ])
              ]),
              h('tbody', reportData.map((row, index) =>
                h('tr', {
                  key: index,
                  style: { borderBottom: index < reportData.length - 1 ? '1px solid #F3F4F6' : 'none' }
                }, [
                  h('td', { style: { padding: '14px 16px', fontSize: '12px', color: '#1A1F2E', fontWeight: row.category ? 600 : 400 } }, row.category),
                  h('td', { style: { padding: '14px 16px', fontSize: '12px', color: '#6B7280' } }, row.topic),
                  h('td', { style: { padding: '14px 16px', fontSize: '12px', color: '#6B7280' } }, row.impact),
                  h('td', { style: { padding: '14px 16px', fontSize: '12px', color: '#6B7280' } }, row.stakeholder)
                ])
              ))
            ])
          ])
        }
      })

    case 'timeline':
      return defineComponent({
        props: ['theme'],
        render() {
          const filtered = reportData.filter(d => d.category)
          return h('div', {
            style: { background: '#FFFFFF', borderRadius: '12px', padding: '24px' }
          }, [
            h('div', {
              class: 'flex items-center justify-between gap-4'
            }, filtered.map((row, index) =>
              h('div', { key: index, class: 'flex-1' }, [
                h('div', {
                  style: {
                    background: this.theme.gradient,
                    borderRadius: '12px',
                    padding: '20px',
                    position: 'relative',
                    minHeight: '160px',
                    display: 'flex',
                    flexDirection: 'column'
                  }
                }, [
                  h('div', { style: { fontSize: '24px', fontWeight: 700, color: '#FFFFFF', marginBottom: '8px' } }, String(index + 1).padStart(2, '0')),
                  h('div', { style: { fontSize: '13px', fontWeight: 600, color: '#FFFFFF', marginBottom: '8px' } }, row.category),
                  h('div', { style: { fontSize: '11px', color: 'rgba(255,255,255,0.9)', lineHeight: '1.5' } }, row.topic)
                ])
              ])
            ))
          ])
        }
      })

    case 'cards':
      return defineComponent({
        props: ['theme'],
        render() {
          const filtered = reportData.filter(d => d.category)
          return h('div', { class: 'grid grid-cols-2 gap-4' }, filtered.map((row, index) =>
            h('div', {
              key: index,
              class: 'hover:shadow-lg',
              style: {
                background: '#FFFFFF',
                border: `2px solid ${this.theme.tableBorder}`,
                borderRadius: '12px',
                padding: '20px',
                transition: 'all 0.3s'
              }
            }, [
              h('div', {
                style: {
                  width: '40px',
                  height: '40px',
                  borderRadius: '8px',
                  background: this.theme.gradient,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '12px'
                }
              }, [
                h('span', { style: { fontSize: '16px', fontWeight: 700, color: '#FFFFFF' } }, String(index + 1).padStart(2, '0'))
              ]),
              h('h3', { style: { fontSize: '14px', fontWeight: 600, color: this.theme.primaryColor, marginBottom: '8px' } }, row.category),
              h('p', { style: { fontSize: '12px', color: '#6B7280', marginBottom: '8px', lineHeight: '1.5' } }, row.topic),
              h('p', { style: { fontSize: '11px', color: '#9CA3AF', lineHeight: '1.5' } }, row.impact)
            ])
          ))
        }
      })

    case 'matrix':
      return defineComponent({
        props: ['theme'],
        render() {
          const filtered = reportData.filter(d => d.category).slice(0, 4)
          return h('div', {
            style: {
              background: this.theme.tableBorder,
              borderRadius: '12px',
              padding: '32px',
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gridTemplateRows: '1fr 1fr',
              gap: '2px'
            }
          }, filtered.map((row, index) =>
            h('div', {
              key: index,
              style: {
                background: '#FFFFFF',
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center'
              }
            }, [
              h('div', {
                style: {
                  width: '60px',
                  height: '60px',
                  borderRadius: '50%',
                  background: this.theme.gradient,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px'
                }
              }, [
                h('span', { style: { fontSize: '20px', fontWeight: 700, color: '#FFFFFF' } }, String(index + 1).padStart(2, '0'))
              ]),
              h('h3', { style: { fontSize: '13px', fontWeight: 600, color: this.theme.primaryColor, marginBottom: '8px' } }, row.category),
              h('p', { style: { fontSize: '11px', color: '#6B7280', lineHeight: '1.5' } }, row.topic)
            ])
          ))
        }
      })

    case 'list':
      return defineComponent({
        props: ['theme'],
        render() {
          const filtered = reportData.filter(d => d.category)
          return h('div', {
            style: { background: '#FFFFFF', borderRadius: '12px', overflow: 'hidden' }
          }, filtered.map((row, index) =>
            h('div', {
              key: index,
              style: {
                padding: '20px 24px',
                borderBottom: index < filtered.length - 1 ? `1px solid ${this.theme.tableBorder}` : 'none',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '16px'
              }
            }, [
              h('div', {
                style: {
                  width: '36px',
                  height: '36px',
                  borderRadius: '8px',
                  background: this.theme.gradient,
                  flexShrink: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }
              }, [
                h('span', { style: { fontSize: '14px', fontWeight: 700, color: '#FFFFFF' } }, String(index + 1).padStart(2, '0'))
              ]),
              h('div', { class: 'flex-1' }, [
                h('h3', { style: { fontSize: '14px', fontWeight: 600, color: this.theme.primaryColor, marginBottom: '6px' } }, row.category),
                h('p', { style: { fontSize: '12px', color: '#6B7280', marginBottom: '4px' } }, row.topic),
                h('p', { style: { fontSize: '11px', color: '#9CA3AF' } }, row.impact)
              ])
            ])
          ))
        }
      })

    case 'circles':
      return defineComponent({
        props: ['theme'],
        render() {
          const filtered = reportData.filter(d => d.category)
          return h('div', {
            style: {
              background: '#FFFFFF',
              borderRadius: '12px',
              padding: '40px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '32px',
              flexWrap: 'wrap'
            }
          }, filtered.map((row, index) =>
            h('div', {
              key: index,
              class: 'flex flex-col items-center',
              style: { maxWidth: '140px' }
            }, [
              h('div', {
                style: {
                  width: '100px',
                  height: '100px',
                  borderRadius: '50%',
                  background: this.theme.gradient,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '12px',
                  boxShadow: `0 8px 24px ${this.theme.primaryColor}40`
                }
              }, [
                h('span', { style: { fontSize: '24px', fontWeight: 700, color: '#FFFFFF', marginBottom: '4px' } }, String(index + 1).padStart(2, '0'))
              ]),
              h('h3', { style: { fontSize: '12px', fontWeight: 600, color: this.theme.primaryColor, marginBottom: '4px', textAlign: 'center' } }, row.category),
              h('p', { style: { fontSize: '10px', color: '#6B7280', textAlign: 'center', lineHeight: '1.4' } }, row.topic)
            ])
          ))
        }
      })

    default:
      return defineComponent({
        render() {
          return h('div', 'Unknown template')
        }
      })
  }
})
</script>

export const useTabNavigation = () => {
  const activeTab = useState<string>('activeTab', () => 'home')

  const switchTab = (tabId: string) => {
    activeTab.value = tabId
  }

  return {
    activeTab,
    switchTab
  }
}

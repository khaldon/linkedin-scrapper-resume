export const useValidation = () => {
  const validateRequired = (value: any) => {
    if (value === null || value === undefined || value === '') {
      return 'This field is required'
    }
    return null
  }

  const validateEmail = (email: string) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!re.test(email)) {
      return 'Please enter a valid email address'
    }
    return null
  }

  const validateUrl = (url: string) => {
    try {
      new URL(url)
      return null
    } catch (e) {
      return 'Please enter a valid URL'
    }
  }

  const validateFile = (file: File | null, maxSizeMB: number = 5, allowedTypes: string[] = []) => {
    if (!file) return 'Please select a file'
    
    if (file.size > maxSizeMB * 1024 * 1024) {
      return `File size must be less than ${maxSizeMB}MB`
    }

    if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
      return `File type must be one of: ${allowedTypes.join(', ')}`
    }

    return null
  }

  return {
    validateRequired,
    validateEmail,
    validateUrl,
    validateFile
  }
}

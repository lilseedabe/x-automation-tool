/** @type {import('tailwindcss').Config} */
module.exports = {
  // コンテンツファイルの指定
  content: [
    "./frontend/src/**/*.{js,jsx,ts,tsx}",
    "./frontend/public/index.html",
    "./backend/**/*.{py,html}",
  ],
  
  // ダークモード設定
  darkMode: 'class', // 'media' または 'class'
  
  theme: {
    extend: {
      // =============================================================================
      // カラーパレット（X API研究・分析ツール用）
      // =============================================================================
      colors: {
        // プライマリカラー（X/Twitterブランドカラーをベース）
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6', // メインブルー
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        
        // セカンダリカラー（分析・データ用）
        secondary: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        
        // アクセントカラー（AI/分析結果用）
        accent: {
          50: '#fdf4ff',
          100: '#fae8ff',
          200: '#f5d0fe',
          300: '#f0abfc',
          400: '#e879f9',
          500: '#d946ef', // メインパープル
          600: '#c026d3',
          700: '#a21caf',
          800: '#86198f',
          900: '#701a75',
        },
        
        // 成功・エラー・警告カラー
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
        
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        
        // データ可視化用カラー
        chart: {
          blue: '#3b82f6',
          green: '#22c55e',
          yellow: '#f59e0b',
          red: '#ef4444',
          purple: '#d946ef',
          orange: '#f97316',
          teal: '#14b8a6',
          pink: '#ec4899',
        }
      },
      
      // =============================================================================
      // フォント設定
      // =============================================================================
      fontFamily: {
        sans: [
          'Inter',
          'Hiragino Sans',
          'Hiragino Kaku Gothic ProN',
          'Noto Sans JP',
          'Meiryo',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'sans-serif',
        ],
        mono: [
          'JetBrains Mono',
          'Fira Code',
          'Consolas',
          'Monaco',
          'Courier New',
          'monospace',
        ],
      },
      
      // =============================================================================
      // スペーシング拡張
      // =============================================================================
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      
      // =============================================================================
      // ボーダー半径
      // =============================================================================
      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.5rem',
      },
      
      // =============================================================================
      // 影・エフェクト
      // =============================================================================
      boxShadow: {
        'inner-lg': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.1)',
        'glow': '0 0 20px rgba(59, 130, 246, 0.5)',
        'glow-lg': '0 0 30px rgba(59, 130, 246, 0.6)',
      },
      
      // =============================================================================
      // アニメーション
      // =============================================================================
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'pulse-slow': 'pulse 3s infinite',
        'bounce-gentle': 'bounceGentle 2s infinite',
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },
      
      // =============================================================================
      // レスポンシブブレークポイント拡張
      // =============================================================================
      screens: {
        'xs': '475px',
        '3xl': '1600px',
      },
      
      // =============================================================================
      // Z-index 管理
      // =============================================================================
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      },
    },
  },
  
  // =============================================================================
  // プラグイン
  // =============================================================================
  plugins: [
    // フォーム要素のスタイリング
    require('@tailwindcss/forms'),
    
    // タイポグラフィ
    require('@tailwindcss/typography'),
    
    // アスペクト比
    require('@tailwindcss/aspect-ratio'),
    
    // カスタムプラグイン
    function({ addUtilities, addComponents, theme }) {
      // カスタムユーティリティ
      addUtilities({
        '.text-gradient': {
          'background': 'linear-gradient(90deg, #3b82f6, #d946ef)',
          'background-clip': 'text',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
        },
        '.glassmorphism': {
          'backdrop-filter': 'blur(10px)',
          'background': 'rgba(255, 255, 255, 0.1)',
          'border': '1px solid rgba(255, 255, 255, 0.2)',
        },
        '.scrollbar-thin': {
          'scrollbar-width': 'thin',
          'scrollbar-color': theme('colors.gray.400') + ' ' + theme('colors.gray.100'),
        },
        '.scrollbar-none': {
          'scrollbar-width': 'none',
          '-ms-overflow-style': 'none',
          '&::-webkit-scrollbar': {
            'display': 'none',
          },
        },
      });
      
      // カスタムコンポーネント
      addComponents({
        '.btn-primary': {
          'background': theme('colors.primary.500'),
          'color': theme('colors.white'),
          'padding': `${theme('spacing.2')} ${theme('spacing.4')}`,
          'border-radius': theme('borderRadius.md'),
          'font-weight': theme('fontWeight.medium'),
          'transition': 'all 0.2s ease-in-out',
          '&:hover': {
            'background': theme('colors.primary.600'),
            'transform': 'translateY(-1px)',
            'box-shadow': theme('boxShadow.md'),
          },
          '&:active': {
            'transform': 'translateY(0)',
          },
        },
        '.card': {
          'background': theme('colors.white'),
          'border-radius': theme('borderRadius.lg'),
          'box-shadow': theme('boxShadow.md'),
          'padding': theme('spacing.6'),
          'border': `1px solid ${theme('colors.gray.200')}`,
        },
        '.card-dark': {
          'background': theme('colors.gray.800'),
          'border-color': theme('colors.gray.700'),
          'color': theme('colors.gray.100'),
        },
      });
    },
  ],
  
  // =============================================================================
  // Safelist（パージから除外するクラス）
  // =============================================================================
  safelist: [
    // 動的に生成される可能性のあるクラス
    'bg-chart-blue',
    'bg-chart-green',
    'bg-chart-yellow',
    'bg-chart-red',
    'bg-chart-purple',
    'bg-chart-orange',
    'bg-chart-teal',
    'bg-chart-pink',
    // グリッドレイアウト用
    'grid-cols-1',
    'grid-cols-2',
    'grid-cols-3',
    'grid-cols-4',
    'grid-cols-5',
    'grid-cols-6',
    // AI分析結果表示用
    'text-success-500',
    'text-error-500',
    'text-warning-500',
    'bg-success-50',
    'bg-error-50',
    'bg-warning-50',
  ],
};
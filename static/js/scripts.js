window.tailwind.config = {
  darkMode: ['class'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
    },
  },
};

document.addEventListener('DOMContentLoaded', () => {
  const executorsList = document.getElementById('executors-list');
  const description = document.getElementById('description');
  const selectedLanguageElement = document.getElementById('selected-language');
  const codeInput = document.getElementById('code-input');
  const executeButton = document.getElementById('execute-button');
  const outputDiv = document.getElementById('output');
  const resultText = document.getElementById('result-text');
  const currentLanguageElement = document.getElementById('current-language');
  const plotImage = document.getElementById('plot-image');
  const fileUpload = document.getElementById('file-upload');
  const toggleExecutorsButton = document.getElementById('toggle-executors');

  let selectedLanguage = '';

  fetch('/check_executors')
    .then(response => response.json())
    .then(data => {
      description.innerText = '已检测到的执行器:';
      Object.entries(data).forEach(([name, version]) => {
        const button = document.createElement('button');
        button.className = 'bg-blue-500 text-white w-full py-2 px-4 rounded-lg font-medium hover:bg-blue-600 transition duration-300 ease-in-out';
        button.innerHTML = `<strong>${name}</strong><br>版本: ${version}`;
        button.addEventListener('click', () => {
          selectedLanguage = name.toLowerCase().split(' ')[0];
          selectedLanguageElement.innerText = `当前选择的语言: ${name}`;
          currentLanguageElement.innerText = `当前代码执行语言: ${name}`;
        });
        executorsList.appendChild(button);
      });
    });

  toggleExecutorsButton.addEventListener('click', () => {
    executorsList.classList.toggle('hidden');
  });

  executeButton.addEventListener('click', () => {
    const code = codeInput.value;
    if (!selectedLanguage) {
      alert('请选择一种语言');
      return;
    }

    fetch('/execute_code', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ language: selectedLanguage, code }),
    })
      .then(response => response.json())
      .then(data => {
        resultText.innerText = data.output;
        if (data.filename) {
          plotImage.src = `/static/uploads/${data.filename}`;
          plotImage.style.display = 'block';
        } else {
          plotImage.style.display = 'none';
        }
      });
  });

  fileUpload.addEventListener('change', () => {
    const file = fileUpload.files[0];
    if (!file) {
      alert('请选择一个文件');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload_file', {
      method: 'POST',
      body: formData,
    })
      .then(response => response.json())
      .then(data => {
        resultText.innerText = data.output;
        if (data.filename) {
          plotImage.src = `/static/uploads/${data.filename}`;
          plotImage.style.display = 'block';
        } else {
          plotImage.style.display = 'none';
        }
      });
  });

  fetch('/stats')
    .then(response => response.json())
    .then(stats => {
      const statsElement = document.getElementById('stats');
      statsElement.innerHTML = `
        <p>网站开始运行日期: ${stats.start_date}</p>
        <p>网站运行天数: ${stats.days_running} 天</p>
        <p>网站访问量: ${stats.visits} 次</p>
        <p>代码执行次数: ${stats.executions} 次</p>
      `;
    });
});

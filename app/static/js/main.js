let preferences = [];

document.getElementById('preference-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        const value = this.value.trim();
        if (value && !preferences.includes(value)) {
            preferences.push(value);
            updatePreferenceTags();
        }
        this.value = '';
    }
});

function updatePreferenceTags() {
    const container = document.getElementById('preferences-tags');
    container.innerHTML = preferences.map(pref => `
        <span class="preference-tag">
            ${pref}
            <span onclick="removePreference('${pref}')" style="cursor:pointer">×</span>
        </span>
    `).join('');
}

function removePreference(pref) {
    preferences = preferences.filter(p => p !== pref);
    updatePreferenceTags();
}

// 初始化设置
document.addEventListener('DOMContentLoaded', function() {
    const savedPreference = localStorage.getItem('useSolarTerm');
    if (savedPreference !== null) {
        document.getElementById('use-solar-term').checked = savedPreference === 'true';
    }
    
    // 添加开关事件监听
    document.getElementById('use-solar-term').addEventListener('change', saveSolarTermPreference);
    
    loadSettings();
    setupSettingsListeners();
    getCurrentSolarTerm();
});

function setupSettingsListeners() {
    // 设置单选按钮切换事件
    document.querySelectorAll('input[name="ai-engine"]').forEach(radio => {
        radio.addEventListener('change', function() {
            document.getElementById('deepseek-settings').style.display = 
                this.value === 'deepseek' ? 'block' : 'none';
            document.getElementById('ollama-settings').style.display = 
                this.value === 'ollama' ? 'block' : 'none';
        });
    });
}

function toggleSettings() {
    const panel = document.getElementById('settings-panel');
    const overlay = document.querySelector('.overlay');
    panel.classList.toggle('hidden');
    
    if (!overlay) {
        const newOverlay = document.createElement('div');
        newOverlay.className = 'overlay';
        document.body.appendChild(newOverlay);
        newOverlay.addEventListener('click', toggleSettings);
    } else {
        overlay.classList.toggle('active');
    }
}

function saveSettings() {
    const settings = {
        aiEngine: document.querySelector('input[name="ai-engine"]:checked').value,
        deepseekKey: document.getElementById('deepseek-key').value,
        ollamaUrl: document.getElementById('ollama-url').value
    };
    
    localStorage.setItem('aiSettings', JSON.stringify(settings));
    toggleSettings();
    alert('设置已保存！');
}

function loadSettings() {
    const settings = JSON.parse(localStorage.getItem('aiSettings') || '{}');
    
    if (settings.aiEngine) {
        document.querySelector(`input[name="ai-engine"][value="${settings.aiEngine}"]`).checked = true;
    }
    if (settings.deepseekKey) {
        document.getElementById('deepseek-key').value = settings.deepseekKey;
    }
    if (settings.ollamaUrl) {
        document.getElementById('ollama-url').value = settings.ollamaUrl;
    }
    
    // 触发一次change事件来显示/隐藏相应设置
    document.querySelector('input[name="ai-engine"]:checked').dispatchEvent(new Event('change'));
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('search-btn').disabled = true;
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('search-btn').disabled = false;
}

function formatRecommendation(text) {
    // 首先处理 markdown 标记
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');  // 处理加粗
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');  // 处理斜体
    text = text.replace(/###(.*?)$/gm, '<h3>$1</h3>');  // 处理三级标题
    text = text.replace(/##(.*?)$/gm, '<h2>$1</h2>');  // 处理二级标题
    text = text.replace(/#(.*?)$/gm, '<h1>$1</h1>');  // 处理一级标题
    
    // 然后按行处理特殊格式
    return text.split('\n').map(line => {
        line = line.trim();
        if (!line) return '<br>';
        
        // 处理特殊行
        if (line.startsWith('###')) {
            return `<h3 class="recommendation-title">${line.substring(3).trim()}</h3>`;
        } else if (line.startsWith('推荐')) {
            return `<div class="recommendation-header">🍽️ ${line}</div>`;
        } else if (line.startsWith('- **推荐理由**')) {
            return `<div class="reason"><span class="label">💡 推荐理由：</span>${line.replace(/- \*\*推荐理由\*\*：?/, '').trim()}</div>`;
        } else if (line.startsWith('- **符合偏好**')) {
            return `<div class="preference-match"><span class="label">✨ 符合偏好：</span>${line.replace(/- \*\*符合偏好\*\*：?/, '').trim()}</div>`;
        } else if (line.startsWith('- **搭配建议**')) {
            return `<div class="suggestion"><span class="label">🔄 搭配建议：</span>${line.replace(/- \*\*搭配建议\*\*：?/, '').trim()}</div>`;
        } else if (line.startsWith('- **餐厅推荐**')) {
            return `<div class="restaurant"><span class="label">🏪 餐厅推荐：</span>${line.replace(/- \*\*餐厅推荐\*\*：?/, '').trim()}</div>`;
        } else if (line.startsWith('- **组合方式**')) {
            return `<div class="combination"><span class="label">🔀 组合方式：</span>${line.replace(/- \*\*组合方式\*\*：?/, '').trim()}</div>`;
        } else if (line.startsWith('[') && line.endsWith(']')) {
            return `<div class="category-title">${line}</div>`;
        } else if (line.startsWith('-')) {
            return `<div class="list-item">${line.substring(1).trim()}</div>`;
        }
        
        return `<p>${line}</p>`;
    }).join('');
}

// 添加获取节气的函数
async function getCurrentSolarTerm() {
    try {
        const response = await fetch('/api/solar-term');
        const data = await response.json();
        const termElement = document.getElementById('current-term');
        
        if (data.success && data.term && data.term !== '未知') {
            termElement.innerHTML = `<strong>${data.term}</strong>`;
            termElement.classList.remove('no-term');
            termElement.classList.add('has-term');
        } else {
            termElement.textContent = '节气获取失败';
            termElement.classList.remove('has-term');
            termElement.classList.add('no-term');
            console.error('节气获取失败:', data.error || '未知错误');
        }
    } catch (error) {
        console.error('节气API调用失败:', error);
        const termElement = document.getElementById('current-term');
        termElement.textContent = '节气获取失败';
        termElement.classList.remove('has-term');
        termElement.classList.add('no-term');
    }
}

// 添加节气开关状态保存
function saveSolarTermPreference() {
    const useSolarTerm = document.getElementById('use-solar-term').checked;
    localStorage.setItem('useSolarTerm', useSolarTerm);
}

// 添加节气开关状态变化监听
document.getElementById('use-solar-term').addEventListener('change', function(e) {
    const statusText = document.querySelector('.toggle-status');
    if (e.target.checked) {
        statusText.textContent = '按节气推荐';
        statusText.style.color = '#4CAF50';
    } else {
        statusText.textContent = '不按节气推荐';
        statusText.style.color = '#94a3b8';
    }
});

// 修改推荐请求函数
async function getRecommendations() {
    const location = document.getElementById('location').value;
    const settings = JSON.parse(localStorage.getItem('aiSettings') || '{}');
    const useSolarTerm = document.getElementById('use-solar-term').checked;
    
    if (!location) {
        alert('请输入位置');
        return;
    }
    
    if (!settings.aiEngine) {
        alert('请先在设置中选择 AI 引擎');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                location,
                preferences,
                use_solar_term: useSolarTerm,  // 添加节气选项
                ai_type: settings.aiEngine,
                ai_settings: {
                    deepseek_key: settings.deepseekKey,
                    ollama_url: settings.ollamaUrl
                }
            })
        });
        
        const data = await response.json();
        
        // 更新显示结果
        document.getElementById('local-foods-list').innerHTML = 
            data.local_foods.map(food => `<li>🍴 ${food}</li>`).join('');
            
        document.getElementById('ai-recommendations-list').innerHTML = 
            data.ai_recommendations.map(rec => `<li>${formatRecommendation(rec)}</li>`).join('');
            
    } catch (error) {
        console.error('Error:', error);
        alert('获取推荐失败，请重试');
    } finally {
        hideLoading();
    }
} 
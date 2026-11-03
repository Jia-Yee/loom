// ════════════════════════════════════════════════════════════
//  节点类型定义
// ════════════════════════════════════════════════════════════
const NODE_TYPES = {
  // ── 数据 ──
  dataset: {
    label: '数据集', category: 'data', icon: '📊', color: 'var(--cat-data)',
    codeFile: 'datasets/toy.py',
    inputs: [],
    outputs: [{ name: 'data', label: 'X, y' }],
    config: {
      dataset_name: { type: 'select', label: '数据集', options: ['diabetes', 'breast_cancer', 'california_housing'], default: 'diabetes' },
    },
  },
  csv_upload: {
    label: 'CSV 上传', category: 'data', icon: '📁', color: 'var(--cat-data)',
    codeFile: 'datasets/csv_loader.py',
    inputs: [],
    outputs: [{ name: 'data', label: 'X, y' }],
    config: {
      file: { type: 'file', label: 'CSV 文件', accept: '.csv' },
      target_column: { type: 'string', label: '目标列名' },
      task_type: { type: 'select', label: '任务类型', options: ['regression', 'classification'], default: 'regression' },
    },
  },
  data_analysis: {
    label: '数据分析', category: 'data', icon: '🔍', color: 'var(--cat-data)',
    codeFile: 'server.py',
    inputs: [{ name: 'data', label: 'X, y' }],
    outputs: [{ name: 'summary', label: '统计' }],
    config: {},
  },

  // ── 处理 ──
  split: {
    label: '数据切分', category: 'process', icon: '✂️', color: 'var(--cat-process)',
    codeFile: 'core/runner.py',
    inputs: [{ name: 'data', label: 'X, y' }],
    outputs: [{ name: 'train', label: '训练集' }, { name: 'test', label: '测试集' }],
    config: {
      test_size: { type: 'number', label: '测试集比例', default: 0.2, step: 0.05, min: 0.05, max: 0.5 },
      seed: { type: 'number', label: '随机种子', default: 42 },
    },
  },

  // ── 模型 ──
  model: {
    label: '模型训练', category: 'model', icon: '🧠', color: 'var(--cat-model)',
    codeFile: 'models/linear.py',
    inputs: [{ name: 'train', label: '训练集' }],
    outputs: [{ name: 'model', label: '模型' }],
    config: {
      model_name: { type: 'select', label: '模型', options: ['linear_regression', 'random_forest', 'ridge', 'logistic_regression'], default: 'linear_regression' },
    },
  },
  search: {
    label: '超参搜索', category: 'model', icon: '⚙️', color: 'var(--cat-model)',
    codeFile: 'core/runner.py',
    inputs: [{ name: 'model', label: '模型' }],
    outputs: [{ name: 'best_model', label: '最优模型' }],
    config: {
      n_iter: { type: 'number', label: '迭代次数', default: 10, min: 1, max: 100 },
      cv: { type: 'number', label: '交叉验证折数', default: 5, min: 2, max: 20 },
    },
  },

  // ── 评估 ──
  metric: {
    label: '评估指标', category: 'eval', icon: '📈', color: 'var(--cat-eval)',
    codeFile: 'core/runner.py',
    inputs: [{ name: 'model', label: '模型' }, { name: 'test', label: '测试集' }],
    outputs: [{ name: 'metrics', label: '指标' }],
    config: {},
  },
  comparison: {
    label: '模型对比', category: 'eval', icon: '🏆', color: 'var(--cat-eval)',
    codeFile: 'core/runner.py',
    inputs: [{ name: 'metrics', label: '指标列表' }],
    outputs: [],
    config: {
      select_best: { type: 'checkbox', label: '自动选优', default: true },
    },
  },

  // ── LLM ──
  llm_pre: {
    label: '训练前 LLM 分析', category: 'llm', icon: '🤖', color: 'var(--cat-llm)',
    codeFile: 'core/llm_analyzer.py',
    inputs: [{ name: 'data', label: 'X, y' }],
    outputs: [{ name: 'analysis', label: '分析' }],
    config: {},
  },
  llm_post: {
    label: '结果解读', category: 'llm', icon: '💬', color: 'var(--cat-llm)',
    codeFile: 'core/llm_analyzer.py',
    inputs: [{ name: 'metrics', label: '指标' }],
    outputs: [{ name: 'interpretation', label: '解读' }],
    config: {
      llm_post_scope: { type: 'select', label: '解读范围', options: ['all', 'best'], default: 'all' },
    },
  },
  llm_config: {
    label: 'LLM 配置', category: 'llm', icon: '⚙️', color: 'var(--cat-llm)',
    codeFile: 'core/llm_analyzer.py',
    inputs: [],
    outputs: [{ name: 'config', label: '配置' }],
    config: {
      provider: { type: 'select', label: 'Provider', options: ['', 'deepseek', 'ollama'], default: '' },
      api_key: { type: 'password', label: 'API Key' },
      base_url: { type: 'string', label: 'Base URL' },
      model: { type: 'string', label: '模型名' },
      timeout: { type: 'number', label: '超时(秒)', default: 120 },
    },
  },

  // ── 输出 ──
  output: {
    label: '保存结果', category: 'output', icon: '💾', color: 'var(--cat-output)',
    codeFile: 'core/store.py',
    inputs: [{ name: 'result', label: '结果' }],
    outputs: [],
    config: {},
  },
};

const CATEGORIES = {
  data: { label: '数据', icon: '📥' },
  process: { label: '处理', icon: '🔧' },
  model: { label: '模型', icon: '🧠' },
  eval: { label: '评估', icon: '📊' },
  llm: { label: 'LLM', icon: '🤖' },
  output: { label: '输出', icon: '💾' },
};

// ════════════════════════════════════════════════════════════
//  状态
// ════════════════════════════════════════════════════════════
let nodes = [];  // {id, type, x, y, config, status, display}
let edges = [];  // {source, target}
let selectedNode = null;
let nodeIdCounter = 0;
let draggingNode = null;
let connectingPort = null;

// ════════════════════════════════════════════════════════════
//  左栏：节点库渲染
// ════════════════════════════════════════════════════════════
function renderNodeLibrary(filter = '') {
  const container = document.getElementById('nodeLibrary');
  container.innerHTML = '';
  for (const [catKey, cat] of Object.entries(CATEGORIES)) {
    const types = Object.entries(NODE_TYPES).filter(([t, def]) => {
      if (def.category !== catKey) return false;
      if (filter && !def.label.toLowerCase().includes(filter.toLowerCase()) && !t.includes(filter.toLowerCase())) return false;
      return true;
    });
    if (types.length === 0) continue;

    const catDiv = document.createElement('div');
    catDiv.className = 'node-category';
    catDiv.innerHTML = `
      <div class="cat-header" onclick="this.parentElement.classList.toggle('collapsed')">
        <span class="cat-icon">${cat.icon}</span>
        <span>${cat.label}</span>
        <span class="cat-count">${types.length}</span>
      </div>
      <div class="cat-items"></div>
    `;
    const itemsDiv = catDiv.querySelector('.cat-items');
    types.forEach(([type, def]) => {
      const item = document.createElement('div');
      item.className = 'node-item';
      item.draggable = true;
      item.innerHTML = `
        <span class="node-dot" style="background:${def.color}"></span>
        <span>${def.icon}</span>
        <span>${def.label}</span>
      `;
      item.ondragstart = (e) => {
        e.dataTransfer.setData('node-type', type);
      };
      itemsDiv.appendChild(item);
    });
    container.appendChild(catDiv);
  }
}

function filterNodes(val) { renderNodeLibrary(val); }

// ════════════════════════════════════════════════════════════
//  画布：拖拽放置
// ════════════════════════════════════════════════════════════
const canvas = document.getElementById('canvas');

canvas.ondragover = (e) => { e.preventDefault(); canvas.classList.add('drag-over'); };
canvas.ondragleave = (e) => { if (e.target === canvas) canvas.classList.remove('drag-over'); };
canvas.ondrop = (e) => {
  e.preventDefault();
  canvas.classList.remove('drag-over');
  const type = e.dataTransfer.getData('node-type');
  if (!type || !NODE_TYPES[type]) return;
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left - 100;
  const y = e.clientY - rect.top - 20;
  addNode(type, x, y);
};

function addNode(type, x, y) {
  const def = NODE_TYPES[type];
  const id = `node-${++nodeIdCounter}`;
  const config = {};
  // 初始化默认配置
  for (const [key, cfg] of Object.entries(def.config || {})) {
    config[key] = cfg.default !== undefined ? cfg.default : (cfg.type === 'checkbox' ? false : '');
  }
  const node = { id, type, x, y, config, status: 'idle', display: {} };
  nodes.push(node);
  renderCanvas();
  selectNode(id);
  addLog(`添加节点: ${def.label} (${id})`);
}

function renderCanvas() {
  // 清除旧节点
  canvas.querySelectorAll('.canvas-node').forEach(n => n.remove());
  document.getElementById('canvasEmpty').style.display = nodes.length === 0 ? 'block' : 'none';

  nodes.forEach(node => {
    const def = NODE_TYPES[node.type];
    const el = document.createElement('div');
    el.className = `canvas-node status-${node.status}`;
    if (selectedNode === node.id) el.classList.add('selected');
    el.style.left = `${node.x}px`;
    el.style.top = `${node.y}px`;
    el.id = `cn-${node.id}`;

    // 标题栏
    const titleColor = def.color.startsWith('var') ? '' : def.color;
    el.innerHTML = `
      <div class="node-title" style="background:${def.color}">
        <span>${def.icon}</span>
        <span>${def.label}</span>
      </div>
      <div class="node-body">${renderNodeBody(node)}</div>
      <div class="node-ports">
        <div style="display:flex;gap:4px;align-items:center;">
          ${(def.inputs||[]).map(p => `<div class="port input" data-node="${node.id}" data-port="${p.name}" data-dir="input" title="${p.label}"></div>`).join('')}
        </div>
        <div style="display:flex;gap:4px;align-items:center;">
          ${(def.outputs||[]).map(p => `<div class="port output" data-node="${node.id}" data-port="${p.name}" data-dir="output" title="${p.label}"></div>`).join('')}
        </div>
      </div>
    `;
    el.onmousedown = (e) => startDrag(node, e);
    el.onclick = (e) => { e.stopPropagation(); selectNode(node.id); };
    canvas.appendChild(el);
  });

  // 端口连线事件
  canvas.querySelectorAll('.port').forEach(port => {
    port.onmousedown = (e) => { e.stopPropagation(); startConnect(port, e); };
  });

  renderEdges();
}

function renderNodeBody(node) {
  const def = NODE_TYPES[node.type];
  const d = node.display || {};
  const statusIcons = { idle: '', success: '✅', running: '⏳', failed: '❌', skipped: '⏭️' };

  let body = '';
  switch (node.type) {
    case 'dataset':
      body = `<div>${d.n_samples || '?'} 样本 × ${d.n_features || '?'} 特征</div>`;
      if (d.feature_names) body += `<div style="font-size:0.65rem;opacity:0.7;">${d.feature_names.slice(0,3).join(', ')}...</div>`;
      break;
    case 'split':
      body = `<div>test_size=${node.config.test_size}</div><div>seed=${node.config.seed}</div>`;
      if (d.n_train) body += `<div style="margin-top:2px;">训练${d.n_train}/测试${d.n_test}</div>`;
      break;
    case 'model':
      body = `<div>${node.config.model_name}</div>`;
      if (d.params) body += `<div style="font-size:0.65rem;opacity:0.7;">${Object.entries(d.params).slice(0,2).map(([k,v])=>`${k}=${typeof v==='number'?v.toFixed(3):v}`).join(', ')}</div>`;
      break;
    case 'metric':
      body = Object.entries(d).filter(([k])=>k!=='model_name').map(([k,v])=>`${k}=${typeof v==='number'?v.toFixed(4):v}`).join('<br>') || '等待评估';
      break;
    case 'llm_pre':
    case 'llm_post':
      if (d.content) body = `<div style="max-height:60px;overflow-y:auto;">${escapeHTML(d.content).slice(0,150)}...</div>`;
      else body = '等待分析';
      break;
    case 'comparison':
      if (d.models) body = d.models.map(m=>`${m.is_best?'⭐':''}${m.model_name}`).join('<br>');
      else body = '等待对比';
      break;
    case 'llm_config':
      body = `<div>${node.config.provider || '未配置'}</div>`;
      if (node.config.model) body += `<div style="font-size:0.65rem;opacity:0.7;">${node.config.model}</div>`;
      break;
    default:
      body = '';
  }
  if (statusIcons[node.status]) body = `<div>${statusIcons[node.status]} ${body}</div>`;
  return body;
}

// ════════════════════════════════════════════════════════════
//  画布：拖拽节点
// ════════════════════════════════════════════════════════════
function startDrag(node, e) {
  if (e.target.classList.contains('port')) return;
  selectedNode = node.id;
  const el = document.getElementById(`cn-${node.id}`);
  const startX = e.clientX, startY = e.clientY;
  const origX = node.x, origY = node.y;
  el.classList.add('dragging');

  const onMove = (e) => {
    node.x = origX + (e.clientX - startX);
    node.y = origY + (e.clientY - startY);
    el.style.left = `${node.x}px`;
    el.style.top = `${node.y}px`;
    renderEdges();
  };
  const onUp = () => {
    el.classList.remove('dragging');
    document.removeEventListener('mousemove', onMove);
    document.removeEventListener('mouseup', onUp);
    selectNode(node.id);
  };
  document.addEventListener('mousemove', onMove);
  document.addEventListener('mouseup', onUp);
}

// ════════════════════════════════════════════════════════════
//  画布：连线
// ════════════════════════════════════════════════════════════
function startConnect(port, e) {
  const nodeId = port.dataset.node;
  const portName = port.dataset.port;
  const dir = port.dataset.dir;
  if (dir !== 'output') return;  // 只能从输出拉到输入

  const onMove = (e) => {
    renderEdges(e);
  };
  const onUp = (e) => {
    document.removeEventListener('mousemove', onMove);
    document.removeEventListener('mouseup', onUp);
    // 检查是否落在输入端口上
    const target = document.elementFromPoint(e.clientX, e.clientY);
    if (target && target.classList.contains('port') && target.dataset.dir === 'input') {
      const targetNode = target.dataset.node;
      if (targetNode !== nodeId) {
        // 避免重复连线
        if (!edges.some(ed => ed.source === nodeId && ed.target === targetNode)) {
          edges.push({ source: nodeId, target: targetNode });
          addLog(`连线: ${nodeId} → ${targetNode}`);
        }
      }
    }
    renderEdges();
  };
  document.addEventListener('mousemove', onMove);
  document.addEventListener('mouseup', onUp);
}

function renderEdges(tempEnd = null) {
  const svg = document.getElementById('edgeLayer');
  // 清除旧路径（保留 defs）
  svg.querySelectorAll('path').forEach(p => p.remove());

  const rect = canvas.getBoundingClientRect();
  svg.setAttribute('width', rect.width);
  svg.setAttribute('height', rect.height);

  edges.forEach(edge => {
    const s = document.getElementById(`cn-${edge.source}`);
    const t = document.getElementById(`cn-${edge.target}`);
    if (!s || !t) return;
    const x1 = s.offsetLeft + s.offsetWidth;
    const y1 = s.offsetTop + s.offsetHeight / 2;
    const x2 = t.offsetLeft;
    const y2 = t.offsetTop + t.offsetHeight / 2;
    const mx = (x1 + x2) / 2;
    svg.appendChild(createPath(x1, y1, mx, y1, mx, y2, x2, y2));
  });

  // 临时连线（拖拽中）
  if (tempEnd) {
    const s = document.getElementById(`cn-${selectedNode}`);
    if (s) {
      const x1 = s.offsetLeft + s.offsetWidth;
      const y1 = s.offsetTop + s.offsetHeight / 2;
      const x2 = tempEnd.clientX - rect.left;
      const y2 = tempEnd.clientY - rect.top;
      const mx = (x1 + x2) / 2;
      const path = createPath(x1, y1, mx, y1, mx, y2, x2, y2);
      path.setAttribute('stroke-dasharray', '4,4');
      path.setAttribute('opacity', '0.5');
      svg.appendChild(path);
    }
  }
}

function createPath(x1, y1, cx1, cy1, cx2, cy2, x2, y2) {
  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  path.setAttribute('d', `M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`);
  path.setAttribute('marker-end', 'url(#arrow)');
  return path;
}

// ════════════════════════════════════════════════════════════
//  右栏：参数配置面板
// ════════════════════════════════════════════════════════════
function selectNode(id) {
  selectedNode = id;
  renderCanvas();
  renderConfigPanel();
}

function renderConfigPanel() {
  const panel = document.getElementById('configPanel');
  const title = document.getElementById('configTitle');
  if (!selectedNode) {
    title.textContent = '参数配置';
    panel.innerHTML = '<div class="config-empty">点击画布上的节点查看参数</div>';
    return;
  }
  const node = nodes.find(n => n.id === selectedNode);
  if (!node) return;
  const def = NODE_TYPES[node.type];
  title.textContent = `${def.icon} ${def.label}`;

  let html = `<div class="config-section-title">节点信息</div>`;
  html += `<div class="config-group"><label>ID</label><input type="text" value="${node.id}" readonly></div>`;
  html += `<div class="config-group"><label>类型</label><input type="text" value="${node.type}" readonly></div>`;
  html += `<div class="config-group"><label>状态</label><input type="text" value="${node.status}" readonly></div>`;

  // 参数表单
  const configKeys = Object.keys(def.config || {});
  if (configKeys.length > 0) {
    html += `<div class="config-section-title">参数配置</div>`;
    for (const [key, cfg] of Object.entries(def.config)) {
      html += `<div class="config-group"><label>${cfg.label}</label>`;
      const val = node.config[key] !== undefined ? node.config[key] : '';
      if (cfg.type === 'select') {
        html += `<select onchange="updateConfig('${key}', this.value)">`;
        for (const opt of cfg.options) {
          html += `<option value="${opt}" ${val === opt ? 'selected' : ''}>${opt || '— 选择 —'}</option>`;
        }
        html += `</select>`;
      } else if (cfg.type === 'checkbox') {
        html += `<div class="checkbox-row"><input type="checkbox" ${val ? 'checked' : ''} onchange="updateConfig('${key}', this.checked)"><span>${cfg.label}</span></div>`;
      } else if (cfg.type === 'number') {
        html += `<input type="number" value="${val}" step="${cfg.step || 1}" min="${cfg.min || ''}" max="${cfg.max || ''}" onchange="updateConfig('${key}', parseFloat(this.value))">`;
      } else if (cfg.type === 'file') {
        html += `<input type="file" accept="${cfg.accept || ''}" onchange="handleFileUpload(this, '${key}')">`;
      } else if (cfg.type === 'password') {
        html += `<input type="password" value="${val}" onchange="updateConfig('${key}', this.value)" placeholder="${cfg.label}">`;
      } else {
        html += `<input type="text" value="${val}" onchange="updateConfig('${key}', this.value)" placeholder="${cfg.label}">`;
      }
      html += `</div>`;
    }
  }

  // 对应代码
  if (def.codeFile) {
    html += `<div class="code-preview">
      <div class="code-header">
        <span>📄 对应代码: ${def.codeFile}</span>
        <button onclick="loadNodeCode('${def.codeFile}')">查看</button>
      </div>
      <pre id="codePreview" style="display:none;"></pre>
    </div>`;
  }

  // 删除按钮
  html += `<div style="margin-top:16px;"><button class="btn" style="width:100%;color:var(--danger);border-color:var(--danger);" onclick="deleteNode('${node.id}')">🗑 删除节点</button></div>`;

  panel.innerHTML = html;
}

function updateConfig(key, val) {
  if (!selectedNode) return;
  const node = nodes.find(n => n.id === selectedNode);
  if (!node) return;
  node.config[key] = val;
  renderCanvas();
  addLog(`修改参数: ${node.type}.${key} = ${val}`);
}

async function handleFileUpload(input, key) {
  const file = input.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch('/api/upload_csv', { method: 'POST', body: formData });
  const data = await res.json();
  if (data.status === 'success') {
    addLog(`CSV 上传成功: ${data.n_rows} 行 × ${data.columns.length} 列`, 'success');
    updateConfig('_csv_filepath', data.filepath);
    updateConfig('_csv_columns', data.columns);
    // 自动填充目标列
    if (data.columns.length > 0) {
      const lastCol = data.columns[data.columns.length - 1];
      const node = nodes.find(n => n.id === selectedNode);
      if (node && !node.config.target_column) {
        node.config.target_column = lastCol;
        renderConfigPanel();
      }
    }
  } else {
    addLog(`CSV 上传失败: ${data.message}`, 'error');
  }
}

async function loadNodeCode(filepath) {
  const pre = document.getElementById('codePreview');
  if (pre.style.display === 'block') { pre.style.display = 'none'; return; }
  pre.textContent = '加载中...';
  pre.style.display = 'block';
  const res = await fetch(`/api/code/${filepath}`);
  const data = await res.json();
  if (data.status === 'success') {
    pre.textContent = data.content;
  } else {
    pre.textContent = '加载失败: ' + data.message;
  }
}

function deleteNode(id) {
  nodes = nodes.filter(n => n.id !== id);
  edges = edges.filter(e => e.source !== id && e.target !== id);
  selectedNode = null;
  renderCanvas();
  renderConfigPanel();
  addLog(`删除节点: ${id}`);
}

// ════════════════════════════════════════════════════════════
//  运行：按连线关系提取数据流
// ════════════════════════════════════════════════════════════
function getUpstream(nodeId) {
  return edges.filter(e => e.target === nodeId).map(e => nodes.find(n => n.id === e.source)).filter(Boolean);
}

function getUpstreamByType(nodeId, type) {
  const direct = getUpstream(nodeId);
  for (const n of direct) {
    if (n.type === type) return n;
    const found = getUpstreamByType(n.id, type);
    if (found) return found;
  }
  return null;
}

async function runFlow() {
  if (nodes.length === 0) { addLog('画布为空，请从左栏拖拽节点', 'error'); return; }

  const datasetNode = nodes.find(n => (n.type === 'dataset' || n.type === 'csv_upload'));
  if (!datasetNode) { addLog('缺少数据集节点，请拖入一个', 'error'); return; }

  const modelNodes = nodes.filter(n => n.type === 'model');
  if (modelNodes.length === 0) { addLog('缺少模型节点，请拖入至少一个', 'error'); return; }

  // 检查哪些 model 有连线上游
  const connectedModels = modelNodes.filter(m => edges.some(e => e.target === m.id));
  const modelsToRun = connectedModels.length > 0 ? connectedModels : modelNodes;

  const modelNames = modelsToRun.map(n => n.config.model_name).filter(Boolean);
  if (modelNames.length === 0) { addLog('模型节点未选择模型（右栏配置模型名）', 'error'); return; }

  // split: 优先从 model 上游找
  let splitNode = null;
  for (const m of modelsToRun) {
    splitNode = getUpstreamByType(m.id, 'split');
    if (splitNode) break;
  }
  if (!splitNode) splitNode = nodes.find(n => n.type === 'split');

  // LLM config: 从 llm_pre/llm_post 上游找
  let llmConfigNode = null;
  const llmPre = nodes.find(n => n.type === 'llm_pre');
  const llmPostNode = nodes.find(n => n.type === 'llm_post');
  if (llmPre) llmConfigNode = getUpstreamByType(llmPre.id, 'llm_config');
  if (!llmConfigNode && llmPostNode) llmConfigNode = getUpstreamByType(llmPostNode.id, 'llm_config');
  if (!llmConfigNode) llmConfigNode = nodes.find(n => n.type === 'llm_config');

  const searchNode = nodes.find(n => n.type === 'search');
  const comparisonNode = nodes.find(n => n.type === 'comparison');

  const body = {
    model_names: modelNames,
    dataset_name: datasetNode.config.dataset_name || 'diabetes',
    test_size: splitNode ? (parseFloat(splitNode.config.test_size) || 0.2) : 0.2,
    seed: splitNode ? (parseInt(splitNode.config.seed) || 42) : 42,
    select_best: comparisonNode ? (comparisonNode.config.select_best === true || comparisonNode.config.select_best === 'true') : false,
    llm_post_scope: llmPostNode ? (llmPostNode.config.llm_post_scope || 'all') : 'all',
    search: !!searchNode,
    n_iter: searchNode ? (parseInt(searchNode.config.n_iter) || 10) : 10,
    cv: searchNode ? (parseInt(searchNode.config.cv) || 5) : 5,
  };

  // LLM 配置：从全局配置读取（localStorage）
  const llmCfg = getLLMConfig();
  if (llmCfg.provider) {
    body.llm_provider = llmCfg.provider;
    body.llm_api_key = llmCfg.api_key;
    body.llm_base_url = llmCfg.base_url;
    body.llm_model = llmCfg.model;
    body.llm_timeout = llmCfg.timeout;
  }

  if (datasetNode.type === 'csv_upload' && datasetNode.config.filepath) {
    body.csv_config = {
      name: datasetNode.config.dataset_name || 'csv_data',
      filepath: datasetNode.config.filepath,
      target_column: datasetNode.config.target_column || '',
      task_type: datasetNode.config.task_type || 'regression',
    };
  }

  addLog(`启动流水线: 模型=${modelNames}, 数据集=${body.dataset_name}`);
  if (llmCfg.provider) addLog(`LLM: ${llmCfg.provider}/${llmCfg.model}`);
  if (splitNode) addLog(`切分: test_size=${body.test_size}, seed=${body.seed}`);
  if (searchNode) addLog(`搜索: n_iter=${body.n_iter}, cv=${body.cv}`);
  setStatus('running', '运行中...');
  document.getElementById('btnRun').disabled = true;

  modelsToRun.forEach(n => n.status = 'running');
  if (datasetNode) datasetNode.status = 'running';
  if (splitNode) splitNode.status = 'running';
  if (llmPre) llmPre.status = 'running';
  if (llmPostNode) llmPostNode.status = 'running';
  if (comparisonNode) comparisonNode.status = 'running';
  if (searchNode) searchNode.status = 'running';
  renderCanvas();

  try {
    const res = await fetch('/api/run_stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const data = JSON.parse(line.slice(6));

        if (data.type === 'step') {
          const icon = { running: '⏳', success: '✅', failed: '❌', skipped: '⏭️' }[data.status] || '⏳';
          addLog(`${icon} [${data.step}] ${data.message}`, data.status === 'failed' ? 'error' : data.status === 'success' ? 'success' : '');
          // 更新对应节点状态
          updateNodeStatus(data);
        } else if (data.type === 'done') {
          // 用后端返回的 nodes/edges 更新画布
          if (data.nodes) {
            // 保留用户画布上的位置，用后端结果更新状态和 display
            const newNodes = [];
            for (const srvNode of data.nodes) {
              const existing = nodes.find(ln => ln.id === srvNode.id || ln.type === srvNode.type);
              const def = NODE_TYPES[srvNode.type] || { color: '#666' };
              newNodes.push({
                ...srvNode,
                color: def.color,
                x: existing ? existing.x : (srvNode.position?.x || 0),
                y: existing ? existing.y : (srvNode.position?.y || 0),
                config: existing ? existing.config : {},
              });
            }
            nodes = newNodes;
            edges = data.edges.map(e => ({ source: e.source, target: e.target }));
          }
          renderCanvas();
          setStatus('success', '完成');
          addLog(`\n✅ 流水线完成！run_id=${data.run_id}`, 'success');
          if (data.best_model) addLog(`⭐ 最优模型: ${data.best_model}`, 'success');
          for (const [name, m] of Object.entries(data.metrics)) {
            const s = Object.entries(m).map(([k,v]) => `${k}=${v.toFixed(4)}`).join('  ');
            addLog(`  ${name}: ${s}`);
          }
        } else if (data.type === 'error') {
          addLog(`❌ ${data.message}`, 'error');
          setStatus('error', '错误');
          nodes.forEach(n => { if (n.status === 'running') n.status = 'failed'; });
          renderCanvas();
        }
      }
    }
  } catch (e) {
    addLog(`❌ 请求失败: ${e.message}`, 'error');
    setStatus('error', '错误');
  } finally {
    document.getElementById('btnRun').disabled = false;
  }
}

function updateNodeStatus(data) {
  // 根据 step 更新画布节点状态
  const stepMap = {
    'dataset': 'dataset', 'split': 'split', 'train': 'model', 'search': 'search',
    'metric': 'metric', 'llm_pre': 'llm_pre', 'llm_post': 'llm_post',
    'select_best': 'comparison',
  };
  const nodeType = stepMap[data.step];
  if (nodeType) {
    const node = nodes.find(n => n.type === nodeType);
    if (node) {
      node.status = data.status;
      renderCanvas();
    }
  }
}

// ════════════════════════════════════════════════════════════
//  工具函数
// ════════════════════════════════════════════════════════════
function clearCanvas() {
  if (nodes.length > 0 && !confirm('确定清空画布？')) return;
  nodes = []; edges = []; selectedNode = null;
  renderCanvas(); renderConfigPanel();
  addLog('画布已清空');
}

function resetLayout() {
  // 按拓扑顺序排列
  const xStep = 250, yStep = 120;
  const cols = {};
  nodes.forEach((n, i) => {
    n.x = (i % 4) * xStep;
    n.y = Math.floor(i / 4) * yStep;
  });
  renderCanvas();
  addLog('布局已重置');
}

function autoLayout() {
  // 简单自动排列：按类型分列
  const colMap = { dataset: 0, csv_upload: 0, llm_config: 0, llm_pre: 1, data_analysis: 1, split: 2, model: 3, search: 4, metric: 5, llm_post: 6, comparison: 7, output: 8 };
  const colCounts = {};
  nodes.forEach(n => {
    const col = colMap[n.type] || 0;
    if (!colCounts[col]) colCounts[col] = 0;
    n.x = col * 250;
    n.y = colCounts[col] * 130;
    colCounts[col]++;
  });
  renderCanvas();
  addLog('已自动排列');
}

function addLog(text, level = '') {
  const panel = document.getElementById('logPanel');
  const line = document.createElement('div');
  line.className = `log-line ${level}`;
  line.textContent = text;
  panel.appendChild(line);
  panel.scrollTop = panel.scrollHeight;
}

function clearLog() {
  document.getElementById('logPanel').innerHTML = '<div class="log-line">日志已清空。</div>';
}

function setStatus(cls, text) {
  document.getElementById('statusDot').className = `status-dot ${cls}`;
  document.getElementById('statusText').textContent = text;
}

function escapeHTML(str) {
  const d = document.createElement('div');
  d.textContent = str ?? '';
  return d.innerHTML;
}

async function showHistory() {
  const res = await fetch('/api/history?limit=20');
  const data = await res.json();
  let msg = '历史记录:\n';
  if (data.runs.length === 0) msg += '（暂无）';
  data.runs.forEach(r => { msg += `  ${r.run_id} | ${r.dataset_name} | ${r.best_model||'-'}\n`; });
  alert(msg);
}

// 点击画布空白取消选中
canvas.onclick = (e) => {
  if (e.target === canvas || e.target.classList.contains('canvas-empty') || e.target.classList.contains('edge-layer')) {
    selectedNode = null;
    renderCanvas();
    renderConfigPanel();
  }
};

// ════════════════════════════════════════════════════════════
//  初始化
// ════════════════════════════════════════════════════════════
renderNodeLibrary();

// 空画布，用户从左栏拖拽节点
renderCanvas();
updateLLMBadge();

// ════════════════════════════════════════════════════════════
//  Tab 切换
// ════════════════════════════════════════════════════════════
function switchTab(tab) {
  const flow = document.getElementById('flowPanel');
  const chat = document.getElementById('chatPanel');
  const code = document.getElementById('codePanel');
  ['tabFlow','tabChat','tabCode'].forEach(t => document.getElementById(t)?.classList.remove('active'));
  [flow, chat, code].forEach(p => { if(p) p.style.display = 'none'; });
  if (tab === 'flow') { flow.style.display = 'flex'; document.getElementById('tabFlow').classList.add('active'); }
  else if (tab === 'chat') { chat.style.display = 'flex'; document.getElementById('tabChat').classList.add('active'); }
  else if (tab === 'code') { code.style.display = 'flex'; document.getElementById('tabCode').classList.add('active'); if (!codeLoaded) loadFileList(); }
}

// ════════════════════════════════════════════════════════════
//  AI 对话
// ════════════════════════════════════════════════════════════
let chatHistory = [];

async function sendChat() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;

  const includeCode = document.getElementById('chatIncludeCode').checked;
  const includeResults = document.getElementById('chatIncludeResults').checked;

  // 显示用户消息
  appendChatMsg('user', text);
  chatHistory.push({ role: 'user', content: text });
  input.value = '';
  input.style.height = 'auto';

  // 获取 LLM 配置
  const cfg = getLLMConfig();
  if (!cfg.provider) {
    appendChatMsg('assistant', '请先在流程编辑器中配置 LLM（拖入 LLM 配置节点）');
    return;
  }

  // 创建 AI 消息占位
  const aiEl = appendChatMsg('assistant', '');
  let aiText = '';

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: chatHistory,
        provider: cfg.provider,
        api_key: cfg.api_key,
        base_url: cfg.base_url,
        model: cfg.model,
        include_code: includeCode,
        include_results: includeResults,
      }),
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const data = JSON.parse(line.slice(6));
        if (data.type === 'chunk') { aiText += data.content; aiEl.querySelector('.chat-text').textContent = aiText; }
        else if (data.type === 'done') { break; }
        else if (data.type === 'error') { aiEl.querySelector('.chat-text').textContent = '❌ ' + data.message; return; }
      }
    }
    chatHistory.push({ role: 'assistant', content: aiText });
  } catch (e) {
    aiEl.querySelector('.chat-text').textContent = '❌ 请求失败: ' + e.message;
  }
}

function appendChatMsg(role, text) {
  const container = document.getElementById('chatMessages');
  if (container.children.length === 1 && container.children[0].style.textAlign === 'center') {
    container.innerHTML = '';
  }
  const el = document.createElement('div');
  el.className = `chat-msg ${role}`;
  const avatar = role === 'user' ? '🧑' : '🤖';
  el.innerHTML = `<div class="chat-avatar">${avatar}</div><div class="chat-text">${escapeHTML(text)}</div>`;
  container.appendChild(el);
  container.scrollTop = container.scrollHeight;
  return el;
}

function sendSuggestion(text) {
  document.getElementById('chatInput').value = text;
  sendChat();
}

function onChatKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

// ════════════════════════════════════════════════════════════
//  全局 LLM 配置（localStorage 持久化）
// ════════════════════════════════════════════════════════════
function getLLMConfig() {
  try {
    const saved = localStorage.getItem('loom_llm_config');
    if (saved) return JSON.parse(saved);
  } catch(e) {}
  return { provider: '', api_key: '', base_url: '', model: '', timeout: 120 };
}

function saveLLMSettings() {
  const cfg = {
    provider: document.getElementById('llmProviderGlobal').value,
    api_key: document.getElementById('llmApiKeyGlobal').value,
    base_url: document.getElementById('llmBaseUrlGlobal').value,
    model: document.getElementById('llmModelGlobal').value,
    timeout: parseInt(document.getElementById('llmTimeoutGlobal').value) || 120,
  };
  localStorage.setItem('loom_llm_config', JSON.stringify(cfg));
  closeLLMSettings();
  addLog(`LLM 配置已保存: ${cfg.provider || '未配置'}/${cfg.model || '默认'}`, 'success');
  // 更新顶栏状态
  updateLLMBadge();
}

function showLLMSettings() {
  const cfg = getLLMConfig();
  document.getElementById('llmProviderGlobal').value = cfg.provider || '';
  document.getElementById('llmApiKeyGlobal').value = cfg.api_key || '';
  document.getElementById('llmBaseUrlGlobal').value = cfg.base_url || '';
  document.getElementById('llmModelGlobal').value = cfg.model || '';
  document.getElementById('llmTimeoutGlobal').value = cfg.timeout || 120;
  document.getElementById('llmTestResult').innerHTML = '';
  document.getElementById('llmModal').style.display = 'flex';
}

function closeLLMSettings() {
  document.getElementById('llmModal').style.display = 'none';
}

async function testLLMGlobal() {
  const cfg = {
    provider: document.getElementById('llmProviderGlobal').value,
    api_key: document.getElementById('llmApiKeyGlobal').value,
    base_url: document.getElementById('llmBaseUrlGlobal').value,
    model: document.getElementById('llmModelGlobal').value,
    timeout: parseInt(document.getElementById('llmTimeoutGlobal').value) || 120,
  };
  const result = document.getElementById('llmTestResult');
  result.innerHTML = '<span style="color:var(--text-light);">测试中...</span>';
  document.getElementById('btnTestLLM').disabled = true;
  try {
    const res = await fetch('/api/llm_test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cfg),
    });
    const data = await res.json();
    if (data.status === 'success') {
      result.innerHTML = `<span style="color:var(--success);">✅ ${data.message}</span>`;
    } else {
      result.innerHTML = `<span style="color:var(--danger);">❌ ${data.message}</span>`;
    }
  } catch(e) {
    result.innerHTML = `<span style="color:var(--danger);">❌ 请求失败: ${e.message}</span>`;
  }
  document.getElementById('btnTestLLM').disabled = false;
}

function updateLLMBadge() {
  const cfg = getLLMConfig();
  const dot = document.getElementById('statusDot');
  const text = document.getElementById('statusText');
  if (cfg.provider) {
    text.textContent = `LLM: ${cfg.model || cfg.provider}`;
  } else {
    text.textContent = '就绪';
  }
}

// ════════════════════════════════════════════════════════════
//  代码面板
// ════════════════════════════════════════════════════════════
let codeLoaded = false;
let currentCodePath = '';
let originalCode = '';

async function loadFileList() {
  const res = await fetch('/api/code');
  const data = await res.json();
  const list = document.getElementById('fileList');
  list.innerHTML = '';
  const groups = {};
  data.files.forEach(f => {
    const dir = f.path.includes('/') ? f.path.split('/')[0] : '.';
    if (!groups[dir]) groups[dir] = [];
    groups[dir].push(f);
  });
  for (const [dir, files] of Object.entries(groups)) {
    const header = document.createElement('div');
    header.style.cssText = 'padding:6px 16px;font-size:0.7rem;color:var(--text-light);font-weight:600;text-transform:uppercase;';
    header.textContent = dir + '/';
    list.appendChild(header);
    files.forEach(f => {
      const item = document.createElement('div');
      item.style.cssText = 'padding:4px 16px 4px 24px;font-size:0.8rem;cursor:pointer;color:var(--text);';
      item.textContent = f.path.split('/').pop();
      item.onmouseover = () => item.style.background = 'var(--bg)';
      item.onmouseout = () => item.style.background = '';
      item.onclick = () => loadCode(f.path);
      list.appendChild(item);
    });
  }
  codeLoaded = true;
}

async function loadCode(path) {
  currentCodePath = path;
  document.getElementById('codePath').textContent = path;
  document.getElementById('codeStatus').textContent = '加载中...';
  const res = await fetch(`/api/code/${path}`);
  const data = await res.json();
  if (data.status !== 'success') { document.getElementById('codeStatus').textContent = '加载失败'; return; }
  originalCode = data.content;
  document.getElementById('codeContent').textContent = data.content;
  document.getElementById('codeContent').style.display = 'block';
  document.getElementById('codeEditor').style.display = 'none';
  document.getElementById('btnEditCode').style.display = 'inline-block';
  document.getElementById('btnCancelCode').style.display = 'none';
  document.getElementById('btnSaveCode').style.display = 'none';
  document.getElementById('codeStatus').textContent = `${data.lines} 行 · ${data.size} 字符`;
}

function editCode() {
  const editor = document.getElementById('codeEditor');
  editor.value = originalCode;
  document.getElementById('codeContent').style.display = 'none';
  editor.style.display = 'block';
  editor.focus();
  document.getElementById('btnEditCode').style.display = 'none';
  document.getElementById('btnCancelCode').style.display = 'inline-block';
  document.getElementById('btnSaveCode').style.display = 'inline-block';
  document.getElementById('codeStatus').textContent = '编辑中...';
}

function cancelEdit() {
  document.getElementById('codeContent').style.display = 'block';
  document.getElementById('codeEditor').style.display = 'none';
  document.getElementById('btnEditCode').style.display = 'inline-block';
  document.getElementById('btnCancelCode').style.display = 'none';
  document.getElementById('btnSaveCode').style.display = 'none';
  document.getElementById('codeStatus').textContent = '已取消';
}

async function saveCode() {
  const editor = document.getElementById('codeEditor');
  const content = editor.value;
  if (content === originalCode) { document.getElementById('codeStatus').textContent = '无修改'; return; }
  document.getElementById('codeStatus').textContent = '保存中...';
  const res = await fetch(`/api/code/${currentCodePath}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });
  const data = await res.json();
  if (data.status === 'success') {
    originalCode = content;
    document.getElementById('codeContent').textContent = content;
    document.getElementById('codeContent').style.display = 'block';
    editor.style.display = 'none';
    document.getElementById('btnEditCode').style.display = 'inline-block';
    document.getElementById('btnCancelCode').style.display = 'none';
    document.getElementById('btnSaveCode').style.display = 'none';
    document.getElementById('codeStatus').textContent = `✅ ${data.message}`;
  } else {
    document.getElementById('codeStatus').textContent = `❌ ${data.message}`;
  }
}

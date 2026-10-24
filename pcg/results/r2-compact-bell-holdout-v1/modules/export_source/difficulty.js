// A shared authoring scale. Scores describe the required route with its required abilities.
export const DIFFICULTY_SCALE='gunman-rush/module-difficulty/v1';
export const DIFFICULTY_LEVELS=[
  {score:1,name:'休整',guide:'安全通行或休息段，几乎没有失败风险。'},
  {score:2,name:'入门',guide:'单个基础操作，落点宽、时机宽松，失败容易回收。'},
  {score:3,name:'简单',guide:'少量基础操作组合，有明显安全停顿和较高容错。'},
  {score:4,name:'普通',guide:'需要观察机关或调整落点，短动作链，有安全缓冲。'},
  {score:5,name:'中等',guide:'多步操作配合，存在明确的落点或时机要求，容错一般。'},
  {score:6,name:'偏难',guide:'连续操作或移动目标，调整机会减少，失误代价较高。'},
  {score:7,name:'困难',guide:'较长动作链、较窄时机或多重压力，安全停顿较少。'},
  {score:8,name:'高难',guide:'精准落点与紧凑时机持续组合，容错低，需要熟练操作。'},
  {score:9,name:'极难',guide:'多种高压操作长时间串联，补救机会极少。'},
  {score:10,name:'极限',guide:'接近已验证操作上限，持续高精度、几乎不容失误。'}
];
export const emptyDifficulty=()=>({version:1,scale:DIFFICULTY_SCALE,score:null,note:''});
export function validateDifficulty(value){
  if(value==null)return emptyDifficulty();
  if(value.version!==1||value.scale!==DIFFICULTY_SCALE||!(value.score===null||Number.isInteger(value.score)&&value.score>=1&&value.score<=10)||typeof value.note!=='string'||value.note.length>4000)throw Error('难度评分必须为 1～10 的整数，或未评分');
  return {version:1,scale:DIFFICULTY_SCALE,score:value.score,note:value.note};
}
export function difficultySummary(value){
  const d=validateDifficulty(value);
  return d.score===null?'难度未评分':`难度 ${d.score}/10 · ${DIFFICULTY_LEVELS[d.score-1].name}`;
}
export function difficultyChanges(doc){
  if(!doc.source)return null;
  const before=validateDifficulty(doc.baselineDifficulty??doc.source.difficulty),after=validateDifficulty(doc.difficulty);
  return {before,after,changed:JSON.stringify(before)!==JSON.stringify(after)};
}

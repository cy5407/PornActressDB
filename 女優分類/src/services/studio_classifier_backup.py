# -*- coding: utf-8 -*-
"""
片商分類核心功能模組
"""
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class StudioClassificationCore:    """片商分類核心類別"""
    
    def __init__(self, db_manager, code_extractor, studio_identifier, preference_manager):
        self.db_manager = db_manager
        self.code_extractor = code_extractor
        self.studio_identifier = studio_identifier
        self.preference_manager = preference_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.supported_formats = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.m2ts']
        # 初始化大片商集合，用於例外處理邏輯
        self._major_studios = self._identify_major_studios()

    def classify_actresses_by_studio(self, root_path: str, progress_callback=None) -> Dict:
        """按片商分類女優資料夾的主要功能"""
        try:
            root_folder = Path(root_path)
            
            if progress_callback:
                progress_callback(f"🏢 開始片商分類：{root_path}\n")
                progress_callback("=" * 60 + "\n")
            
            # 第一步：掃描所有女優資料夾
            actress_folders = self._scan_actress_folders(root_folder, progress_callback)
            if not actress_folders:
                if progress_callback:
                    progress_callback("🤷 未找到任何女優資料夾\n")
                return {'status': 'success', 'message': '未找到女優資料夾'}
            
            if progress_callback:
                progress_callback(f"📁 發現 {len(actress_folders)} 個女優資料夾\n\n")
            
            # 第二步：重新掃描並更新統計資料
            updated_stats = self._update_actress_statistics(actress_folders, progress_callback)
            
            # 第三步：按片商分類移動
            move_stats = self._move_actresses_by_studio(
                root_folder, updated_stats, progress_callback
            )
            
            return {
                'status': 'success',
                'total_actresses': len(actress_folders),
                'updated_count': len(updated_stats),
                'move_stats': move_stats
            }
            
        except Exception as e:
            self.logger.error(f"片商分類過程中發生錯誤: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def _scan_actress_folders(self, root_folder: Path, progress_callback=None) -> List[Path]:
        """只掃描根目錄第一層的女優資料夾（避免遞迴問題）"""
        actress_folders = []
        
        if progress_callback:
            progress_callback("🔍 正在掃描根目錄的女優資料夾（僅第一層）...\n")
        
        try:
            # 只掃描第一層子目錄，避免遞迴掃描已分類的片商資料夾
            for item in root_folder.iterdir():
                if item.is_dir() and self._is_actress_folder(item):
                    actress_folders.append(item)
                    
            return actress_folders
            
        except Exception as e:
            self.logger.error(f"掃描女優資料夾失敗: {e}")
            return []

    def _is_actress_folder(self, folder_path: Path) -> bool:
        """判斷是否為女優資料夾"""
        folder_name = folder_path.name
        folder_name_upper = folder_name.upper()
        
        # 排除明顯的片商資料夾名稱
        studio_folders = {
            'S1', 'MOODYZ', 'PREMIUM', 'WANZ', 'FALENO', 'ATTACKERS', 
            'E-BODY', 'KAWAII', 'FITCH', 'MADONNA', 'PRESTIGE', 'SOD',
            '單體企劃女優', 'SOLO_ACTRESS', 'INDEPENDENT'
        }
        
        # 排除通用/系統資料夾名稱
        excluded_folders = {
            'AV', 'VIDEO', 'VIDEOS', 'MOVIE', 'MOVIES', 'FILM', 'FILMS',
            'DOWNLOAD', 'DOWNLOADS', 'TEMP', 'TMP', 'CACHE', 'BACKUP',
            'OLD', 'NEW', 'ARCHIVE', 'ARCHIVED', 'UNSORTED', '未分類',
            'OTHER', 'OTHERS', 'MISC', 'MISCELLANEOUS', '其他', '雜項',
            'COLLECTION', 'COLLECTIONS', 'SERIES', '系列', '合集',
            'FOLDER', 'FOLDERS', 'DIR', 'DIRECTORY', 'DATA',
            'UNCENSORED', 'CENSORED', '無碼', '有碼', 'FC2', 'PPV',
            'DELETED', 'TRASH', 'RECYCLE', '回收站', '垃圾桶'
        }
        
        # 組合所有需要排除的資料夾
        all_excluded = studio_folders | excluded_folders
        
        if folder_name_upper in all_excluded:
            return False
        
        # 檢查是否已經在片商資料夾內（避免重複處理）
        parent_name = folder_path.parent.name.upper()
        if parent_name in studio_folders:
            return False
        
        # 排除過短或過長的資料夾名稱（可能不是女優名稱）
        if len(folder_name) < 2 or len(folder_name) > 30:
            return False
        
        # 排除純數字資料夾名稱
        if folder_name.isdigit():
            return False
        
        # 排除看起來像番號的資料夾名稱
        import re
        if re.match(r'^[A-Z]{2,6}-?\d{3,5}[A-Z]?$', folder_name_upper):
            return False
        
        # 檢查資料夾內是否有影片檔案
        try:
            video_count = 0
            total_files = 0
            
            for file_path in folder_path.iterdir():
                if file_path.is_file():
                    total_files += 1
                    if file_path.suffix.lower() in self.supported_formats:
                        video_count += 1
                        
            # 必須至少有一個影片檔案，且影片檔案佔一定比例
            if video_count >= 1 and (total_files <= 10 or video_count / total_files >= 0.3):
                return True
                
        except PermissionError:
            return False
        
        return False

    def _update_actress_statistics(self, actress_folders: List[Path], progress_callback=None) -> Dict[str, Dict]:
        """重新掃描女優資料夾並更新片商統計（使用增強版資料庫分析）"""
        updated_stats = {}
        
        if progress_callback:
            progress_callback("📊 正在使用增強版演算法分析女優片商分佈...\n")
        
        for i, actress_folder in enumerate(actress_folders, 1):
            actress_name = actress_folder.name
            
            try:
                # 使用資料庫的增強分析功能
                analysis_result = self.db_manager.analyze_actress_primary_studio(actress_name, self._major_studios)
                
                if analysis_result['total_videos'] > 0:
                    updated_stats[actress_name] = {
                        'folder_path': actress_folder,
                        'studio_stats': analysis_result['studio_distribution'],
                        'main_studio': analysis_result['primary_studio'],
                        'confidence': analysis_result['confidence'],
                        'total_videos': analysis_result['total_videos'],
                        'recommendation': analysis_result['recommendation'],
                        'analysis_method': 'enhanced_database'
                    }
                    
                    if progress_callback and i % 5 == 0:
                        progress_callback(f"   處理進度: {i}/{len(actress_folders)} ({actress_name}: {analysis_result['primary_studio']} {analysis_result['confidence']}%)\n")
                
                else:
                    # 如果資料庫沒有資料，回退到檔案掃描方式
                    video_files = []
                    for file_path in actress_folder.iterdir():
                        if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                            video_files.append(file_path)
                    
                    if video_files:
                        # 使用檔案掃描方式作為備援
                        studio_stats = self._calculate_studio_distribution(video_files)
                        if studio_stats:
                            main_studio, confidence = self._determine_main_studio(studio_stats)
                            
                            if len(video_files) <= 3 and self._is_major_studio(main_studio):
                                recommendation = 'studio_classification'
                            else:
                                recommendation = 'studio_classification' if confidence >= 60 else 'solo_artist'
                            
                            updated_stats[actress_name] = {
                                'folder_path': actress_folder,
                                'studio_stats': studio_stats,
                                'main_studio': main_studio,
                                'confidence': confidence,
                                'total_videos': len(video_files),
                                'recommendation': recommendation,
                                'analysis_method': 'file_scan_fallback'
                            }
                
            except Exception as e:
                self.logger.error(f"處理女優 {actress_name} 時發生錯誤: {e}")
                continue
        
        if progress_callback:
            progress_callback(f"✅ 完成增強版統計分析，處理了 {len(updated_stats)} 位女優\n")
            
            # 顯示統計摘要
            studio_count = sum(1 for stats in updated_stats.values() if stats['recommendation'] == 'studio_classification')
            solo_count = len(updated_stats) - studio_count
            progress_callback(f"📊 分析結果預覽: {studio_count} 位歸屬特定片商, {solo_count} 位歸為單體企劃\n\n")
        
        return updated_stats

    def _calculate_studio_distribution(self, video_files: List[Path]) -> Dict[str, int]:
        """計算影片檔案的片商分佈"""
        studio_stats = defaultdict(int)
        
        for video_file in video_files:
            # 提取番號
            code = self.code_extractor.extract_code(video_file.name)
            if code:
                # 識別片商
                studio = self.studio_identifier.identify_studio(code)
                if studio and studio != 'UNKNOWN':
                    studio_stats[studio] += 1
        
        return dict(studio_stats)

    def _identify_major_studios(self) -> set:
        major_studios = set()
        studio_patterns = self.studio_identifier.studio_patterns
        
        for studio, prefixes in studio_patterns.items():
            if len(prefixes) >= 3 or studio in ['E-BODY', 'FALENO']:
                major_studios.add(studio)
        
        return major_studios

    def _is_major_studio(self, studio: str) -> bool:
        return studio in self._major_studios

    def _determine_main_studio(self, studio_stats: Dict[str, int]) -> Tuple[str, float]:
        if not studio_stats:
            return 'UNKNOWN', 0.0
        
        total_videos = sum(studio_stats.values())
        if total_videos == 0:
            return 'UNKNOWN', 0.0
        
        main_studio = max(studio_stats.items(), key=lambda x: x[1])
        studio_name, video_count = main_studio
        
        confidence = round((video_count / total_videos) * 100, 1)
        
        if total_videos <= 3 and self._is_major_studio(studio_name):
            confidence = max(confidence, 70.0)
        
        return studio_name, confidence

    def _move_actresses_by_studio(self, root_folder: Path, actress_stats: Dict[str, Dict], 
                                 progress_callback=None) -> Dict:
        """根據片商統計移動女優資料夾"""
        move_stats = {
            'moved': 0,           # 成功移動到片商資料夾
            'exists': 0,          # 目標已存在
            'solo_artist': 0,     # 移動到單體企劃女優
            'failed': 0,          # 移動失敗
            'skipped': 0          # 跳過（來源不存在）
        }
        
        # 取得單體企劃女優資料夾名稱
        solo_folder_name = self.preference_manager.get_solo_folder_name()
        confidence_threshold = self.preference_manager.get_confidence_threshold()
        
        if progress_callback:
            progress_callback("🚚 開始按片商移動女優資料夾...\n")
        
        for actress_name, stats in actress_stats.items():
            try:
                source_folder = stats['folder_path']
                main_studio = stats['main_studio']
                confidence = stats['confidence']
                
                # 檢查來源資料夾是否存在
                if not source_folder.exists():
                    move_stats['skipped'] += 1
                    self.logger.warning(f"來源資料夾不存在，跳過: {source_folder}")
                    if progress_callback:
                        progress_callback(f"⏩ 跳過 {actress_name}: 來源資料夾不存在\n")
                    continue
                
                # 檢查來源是否為目錄
                if not source_folder.is_dir():
                    move_stats['skipped'] += 1
                    self.logger.warning(f"來源不是目錄，跳過: {source_folder}")
                    if progress_callback:
                        progress_callback(f"⏩ 跳過 {actress_name}: 來源不是目錄\n")
                    continue
                
                # 安全檢查：確保來源資料夾在根目錄的第一層
                if source_folder.parent != root_folder:
                    move_stats['skipped'] += 1
                    self.logger.warning(f"來源資料夾不在根目錄第一層，跳過: {source_folder}")
                    if progress_callback:
                        progress_callback(f"⏩ 跳過 {actress_name}: 不在根目錄第一層\n")
                    continue
                
                # 安全檢查：確保這是真的女優資料夾
                if not self._is_actress_folder(source_folder):
                    move_stats['skipped'] += 1
                    self.logger.warning(f"重新檢查發現不是女優資料夾，跳過: {source_folder}")
                    if progress_callback:
                        progress_callback(f"⏩ 跳過 {actress_name}: 重新檢查後不符合女優資料夾條件\n")
                    continue
                
                # 決定目標片商資料夾（使用增強版推薦系統）
                recommendation = stats.get('recommendation', 'solo_artist')
                
                if (recommendation == 'studio_classification' and 
                    confidence >= confidence_threshold and 
                    main_studio != 'UNKNOWN'):
                    target_studio_folder = root_folder / main_studio
                    category = 'studio'
                else:
                    target_studio_folder = root_folder / solo_folder_name
                    category = 'solo'
                
                # 安全檢查：避免移動到自己或循環移動
                target_actress_folder = target_studio_folder / actress_name
                if source_folder == target_studio_folder or target_actress_folder == source_folder:
                    move_stats['skipped'] += 1
                    if progress_callback:
                        progress_callback(f"⏩ 跳過 {actress_name}: 避免循環移動\n")
                    continue
                
                # 建立目標片商資料夾
                try:
                    target_studio_folder.mkdir(exist_ok=True)
                except Exception as e:
                    move_stats['failed'] += 1
                    self.logger.error(f"建立目標資料夾失敗 {target_studio_folder}: {e}")
                    if progress_callback:
                        progress_callback(f"❌ {actress_name}: 無法建立目標資料夾 - {str(e)}\n")
                    continue
                
                # 檢查是否已存在
                if target_actress_folder.exists():
                    move_stats['exists'] += 1
                    if progress_callback:
                        progress_callback(f"⚠️ 已存在: {target_studio_folder.name}/{actress_name}\n")
                    continue
                
                # 執行移動
                try:
                    shutil.move(str(source_folder), str(target_actress_folder))
                    
                    if category == 'solo':
                        move_stats['solo_artist'] += 1
                        if progress_callback:
                            progress_callback(f"🎭 {actress_name} → {solo_folder_name}/ (信心度: {confidence}%)\n")
                    else:
                        move_stats['moved'] += 1
                        if progress_callback:
                            progress_callback(f"✅ {actress_name} → {main_studio}/ (信心度: {confidence}%)\n")
                            
                except FileNotFoundError as e:
                    move_stats['skipped'] += 1
                    self.logger.warning(f"來源檔案不存在，跳過移動 {actress_name}: {e}")
                    if progress_callback:
                        progress_callback(f"⏩ 跳過 {actress_name}: 來源檔案不存在\n")
                        
                except PermissionError as e:
                    move_stats['failed'] += 1
                    self.logger.error(f"權限不足，無法移動 {actress_name}: {e}")
                    if progress_callback:
                        progress_callback(f"❌ {actress_name}: 權限不足 - {str(e)}\n")
                        
                except OSError as e:
                    move_stats['failed'] += 1
                    self.logger.error(f"系統錯誤，無法移動 {actress_name}: {e}")
                    if progress_callback:
                        progress_callback(f"❌ {actress_name}: 系統錯誤 - {str(e)}\n")
                
            except Exception as e:
                move_stats['failed'] += 1
                self.logger.error(f"移動女優 {actress_name} 時發生未預期的錯誤: {e}", exc_info=True)
                if progress_callback:
                    progress_callback(f"❌ {actress_name}: 未預期的錯誤 - {str(e)}\n")
        
        return move_stats

    def get_classification_summary(self, total_actresses: int, move_stats: Dict) -> str:
        """生成片商分類結果摘要"""
        solo_folder_name = self.preference_manager.get_solo_folder_name()
        
        return (f"📊 片商分類完成！\n\n"
               f"  📁 掃描女優總數: {total_actresses}\n"
               f"  ✅ 移動到片商資料夾: {move_stats['moved']}\n"
               f"  🎭 移動到{solo_folder_name}: {move_stats['solo_artist']}\n"
               f"  ⚠️ 目標已存在: {move_stats['exists']}\n"
               f"  ⏩ 跳過處理: {move_stats.get('skipped', 0)}\n"
               f"  ❌ 移動失敗: {move_stats['failed']}\n")

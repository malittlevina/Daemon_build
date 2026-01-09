import shutil
import os
import time
import zipfile

class BackupAgent:
    def __init__(self, src='.', backup_dir='backups', max_backups=5):
        self.src = os.path.abspath(src)
        self.backup_dir = os.path.abspath(backup_dir)
        self.max_backups = max_backups
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Files/Dirs to ignore
        self.ignore_patterns = shutil.ignore_patterns(
            '__pycache__', '*.pyc', '*.git', '.git', 'backups', 'logs', '*.zip', '.DS_Store'
        )

    def create_backup(self, compress=True):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup_name = f"daemon_backup_{timestamp}"
        
        try:
            if compress:
                # Create Zip archive
                archive_path = os.path.join(self.backup_dir, backup_name)
                # shutil.make_archive defaults to zip if format not specified
                # We need to manually handle ignores if using shutil.make_archive directly on a folder 
                # is tricky with ignore patterns. 
                # Instead, let's copy to a temp folder, then zip.
                
                temp_path = os.path.join(self.backup_dir, "temp_staging")
                if os.path.exists(temp_path):
                    shutil.rmtree(temp_path)
                    
                shutil.copytree(self.src, temp_path, ignore=self.ignore_patterns)
                
                final_path = shutil.make_archive(archive_path, 'zip', temp_path)
                shutil.rmtree(temp_path)
                
                result = f"Backup created (compressed): {final_path}"
            else:
                dest = os.path.join(self.backup_dir, backup_name)
                shutil.copytree(self.src, dest, ignore=self.ignore_patterns)
                result = f"Backup created (folder): {dest}"
                
            self._prune_old_backups()
            return result
            
        except Exception as e:
            return f"Backup failed: {e}"

    def restore_backup(self, backup_name=None):
        """
        Restores the system state from a backup.
        If backup_name is None, restores the latest backup.
        """
        try:
            # 1. Select Backup
            if not backup_name:
                files = [f for f in os.listdir(self.backup_dir) if f.endswith('.zip') or os.path.isdir(os.path.join(self.backup_dir, f))]
                if not files:
                    return "No backups found."
                # Sort by time
                files.sort(key=lambda x: os.path.getmtime(os.path.join(self.backup_dir, x)), reverse=True)
                backup_name = files[0]

            backup_path = os.path.join(self.backup_dir, backup_name)
            if not os.path.exists(backup_path):
                return f"Backup '{backup_name}' not found."

            print(f"[BackupAgent] Restoring from {backup_name}...")

            # 2. Safety Check: Verify Integrity (Simple unzip test)
            if zipfile.is_zipfile(backup_path):
                with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                    if zip_ref.testzip() is not None:
                        return "Backup corrupted."
                        
                    # 3. Restore
                    # We extract to current directory (self.src)
                    # Warning: This overwrites files.
                    zip_ref.extractall(self.src)
            else:
                 # It's a directory
                 shutil.copytree(backup_path, self.src, dirs_exist_ok=True)

            return f"System restored from {backup_name}."

        except Exception as e:
            return f"Restore failed: {e}"

    def list_backups(self):
        try:
            files = [f for f in os.listdir(self.backup_dir) if not f.startswith('.')]
            return sorted(files)
        except:
            return []

    def _prune_old_backups(self):
        # List all backups
        files = [os.path.join(self.backup_dir, f) for f in os.listdir(self.backup_dir)]
        files.sort(key=os.path.getmtime)
        
        if len(files) > self.max_backups:
            to_remove = files[:-self.max_backups]
            for f in to_remove:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.remove(f)
            print(f"[BackupAgent] Pruned {len(to_remove)} old backups.")

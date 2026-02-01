import logging
import json
from typing import Dict, Any, Optional
from app.config import config
from app.models import db, Command, Execution
import uuid

# 导入SOARClient
from app.utils.soar_client import SOARClient

logger = logging.getLogger(__name__)

class PlaybookService:
    def __init__(self):
        self.soar_client = SOARClient()

    # ================= 替换开始 (已清理旧代码) =================
    def execute_playbook(self, command: Command) -> Dict[str, Any]:
        """
        执行SOAR剧本 (包含 Mock 逻辑用于演示)
        """
        try:
            # 获取剧本ID和参数
            playbook_id = command.command_entity.get('playbook_id')
            # 有时候 playbook_id 可能是整数或字符串，转字符串处理比较稳
            playbook_id_str = str(playbook_id)
            params = command.command_params or {}
            
            if not playbook_id:
                return {"status": "failed", "message": "缺少剧本ID"}
            
            logger.info(f"正在执行剧本: {playbook_id}, 参数: {params}")

            # ================= MOCK 模拟数据区域 (开始) =================
            # 这里拦截真实的请求，直接返回假数据，骗过系统
            mock_result = None

            # 1. 模拟：IP 资产查询 (对应 query_asset_info_by_ip)
            if "asset" in playbook_id_str or "info" in playbook_id_str:
                target_ip = params.get("ip", "192.168.1.88")
                mock_result = {
                    "status": "success",
                    "data": {
                        "ip": target_ip,
                        "hostname": "finance-server-01", # 假的主机名
                        "owner": "李四 (财务部)",
                        "os": "Ubuntu 22.04 LTS",
                        "location": "核心机房 A-03",
                        "criticality": "High"
                    }
                }

            # 2. 模拟：登录日志查询 (对应 os_login_log_query)
            elif "login" in playbook_id_str or "log" in playbook_id_str:
                mock_result = {
                    "status": "success",
                    "data": [
                        {"time": "2026-01-31 15:00:01", "src_ip": "192.168.1.100", "user": "root", "status": "Failed"},
                        {"time": "2026-01-31 15:00:05", "src_ip": "192.168.1.100", "user": "root", "status": "Failed"},
                        {"time": "2026-01-31 15:00:10", "src_ip": "192.168.1.100", "user": "root", "status": "Failed"},
                        {"time": "2026-01-31 15:04:31", "src_ip": "192.168.1.88", "user": "admin", "status": "Success"}
                    ]
                }
            
            # 3. 兜底模拟：其他所有剧本默认成功
            else:
                mock_result = {"status": "success", "data": "Mock execution completed."}

            # 如果触发了 Mock，直接使用 Mock 结果，不再调用 self.soar_client
            if mock_result:
                import time
                time.sleep(1.5) # 假装跑了一会儿
                result = mock_result # 将 Mock 数据赋值给 result
                logger.info(f"Mock 拦截生效，返回伪造数据: {result}")
            
            # ================= MOCK 模拟数据区域 (结束) =================
            
            else:
                # ------ 下面是原始逻辑（只有 Mock 没命中时才走这里） ------
                activity_id = self.soar_client.execute_playbook(playbook_id, params)
                if not activity_id:
                    raise Exception("剧本执行失败，未获取到活动ID")
                result = self.soar_client.wait_for_completion(activity_id)
                if not result:
                    raise Exception(f"剧本执行超时或失败: {activity_id}")
            
            # 记录执行结果到数据库 (这是必须的，否则UI不会更新状态)
            execution = Execution(
                execution_id=str(uuid.uuid4()),
                command_id=command.command_id,
                action_id=command.action_id,
                task_id=command.task_id,
                event_id=command.event_id,
                round_id=command.round_id,
                execution_result=json.dumps(result),
                execution_summary=f"剧本 {playbook_id} 执行成功 (Mock)",
                execution_status="completed"
            )
            db.session.add(execution)
            db.session.commit()
            
            return {
                "status": "success",
                "message": f"剧本 {playbook_id} 执行成功",
                "data": result
            }
            
        except Exception as e:
            error_msg = f"执行剧本出错: {str(e)}"
            logger.error(error_msg)
            # 记录失败
            execution = Execution(
                execution_id=str(uuid.uuid4()),
                command_id=command.command_id,
                action_id=command.action_id,
                task_id=command.task_id,
                event_id=command.event_id,
                round_id=command.round_id,
                execution_result=json.dumps({"error": str(e)}),
                execution_summary=error_msg,
                execution_status="failed"
            )
            db.session.add(execution)
            db.session.commit()
            return {"status": "failed", "message": error_msg}
    # ================= 替换结束 =================
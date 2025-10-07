#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP文档服务器性能监控和统计系统
监控文档使用情况、AI查询性能和更新频率
"""

import os
import json
import sqlite3
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

@dataclass
class AccessEvent:
    """文档访问事件"""
    timestamp: str
    document_path: str
    access_type: str  # read, write, create, delete
    user_agent: str
    duration_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class AIQueryEvent:
    """AI查询事件"""
    timestamp: str
    query_type: str  # template_generation, code_analysis, quality_check
    project_path: str
    language: str
    duration_ms: int
    tokens_processed: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class UpdateEvent:
    """文档更新事件"""
    timestamp: str
    update_type: str  # automatic, manual, git_hook
    files_changed: int
    trigger: str  # code_change, scheduled, user_action
    success: bool = True
    duration_ms: Optional[int] = None

class MetricsDatabase:
    """指标数据库"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
        self._lock = threading.Lock()
    
    def init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 文档访问表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_access (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    document_path TEXT NOT NULL,
                    access_type TEXT NOT NULL,
                    user_agent TEXT,
                    duration_ms INTEGER,
                    success BOOLEAN NOT NULL,
                    error_message TEXT
                )
            """)
            
            # AI查询表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    project_path TEXT NOT NULL,
                    language TEXT NOT NULL,
                    duration_ms INTEGER NOT NULL,
                    tokens_processed INTEGER,
                    success BOOLEAN NOT NULL,
                    error_message TEXT
                )
            """)
            
            # 文档更新表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    update_type TEXT NOT NULL,
                    files_changed INTEGER NOT NULL,
                    trigger TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    duration_ms INTEGER
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_timestamp ON document_access(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_path ON document_access(document_path)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON ai_queries(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_queries_type ON ai_queries(query_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_updates_timestamp ON document_updates(timestamp)")
            
            conn.commit()
    
    def record_access(self, event: AccessEvent):
        """记录文档访问事件"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO document_access 
                    (timestamp, document_path, access_type, user_agent, duration_ms, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.timestamp, event.document_path, event.access_type, 
                    event.user_agent, event.duration_ms, event.success, event.error_message
                ))
                conn.commit()
    
    def record_ai_query(self, event: AIQueryEvent):
        """记录AI查询事件"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ai_queries 
                    (timestamp, query_type, project_path, language, duration_ms, tokens_processed, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.timestamp, event.query_type, event.project_path, 
                    event.language, event.duration_ms, event.tokens_processed, event.success, event.error_message
                ))
                conn.commit()
    
    def record_update(self, event: UpdateEvent):
        """记录文档更新事件"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO document_updates 
                    (timestamp, update_type, files_changed, trigger, success, duration_ms)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    event.timestamp, event.update_type, event.files_changed, 
                    event.trigger, event.success, event.duration_ms
                ))
                conn.commit()
    
    def get_stats(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """获取统计数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 构建时间过滤条件
            time_filter = ""
            params = []
            if start_date:
                time_filter += " AND timestamp >= ?"
                params.append(start_date)
            if end_date:
                time_filter += " AND timestamp <= ?"
                params.append(end_date)
            
            stats = {}
            
            # 文档访问统计
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_access,
                    COUNT(CASE WHEN success THEN 1 END) as successful_access,
                    AVG(duration_ms) as avg_duration,
                    access_type,
                    COUNT(*) as count
                FROM document_access 
                WHERE 1=1 {time_filter}
                GROUP BY access_type
            """, params)
            
            access_stats = cursor.fetchall()
            stats["document_access"] = {
                "by_type": {row[3]: {"count": row[4], "success_rate": row[1]/row[0] if row[0] > 0 else 0} 
                           for row in access_stats},
                "total_requests": sum(row[0] for row in access_stats),
                "avg_duration_ms": sum(row[2] for row in access_stats if row[2]) / len([r for r in access_stats if r[2]]) if access_stats else 0
            }
            
            # AI查询统计
            cursor.execute(f"""
                SELECT 
                    query_type,
                    COUNT(*) as count,
                    AVG(duration_ms) as avg_duration,
                    AVG(tokens_processed) as avg_tokens,
                    COUNT(CASE WHEN success THEN 1 END) as successful
                FROM ai_queries 
                WHERE 1=1 {time_filter}
                GROUP BY query_type
            """, params)
            
            ai_stats = cursor.fetchall()
            stats["ai_queries"] = {
                "by_type": {
                    row[0]: {
                        "count": row[1],
                        "avg_duration_ms": row[2],
                        "avg_tokens": row[3],
                        "success_rate": row[4] / row[1] if row[1] > 0 else 0
                    } for row in ai_stats
                },
                "total_queries": sum(row[1] for row in ai_stats)
            }
            
            # 文档更新统计
            cursor.execute(f"""
                SELECT 
                    update_type,
                    trigger,
                    COUNT(*) as count,
                    SUM(files_changed) as total_files,
                    AVG(duration_ms) as avg_duration
                FROM document_updates 
                WHERE 1=1 {time_filter}
                GROUP BY update_type, trigger
            """, params)
            
            update_stats = cursor.fetchall()
            stats["document_updates"] = {
                "by_type_and_trigger": {
                    f"{row[0]}_{row[1]}": {
                        "count": row[2],
                        "total_files": row[3],
                        "avg_duration_ms": row[4]
                    } for row in update_stats
                },
                "total_updates": sum(row[2] for row in update_stats)
            }
            
            return stats

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, mcp_root: str, db_path: str = None):
        self.mcp_root = Path(mcp_root)
        self.db_path = db_path or str(self.mcp_root / "metrics.db")
        self.metrics_db = MetricsDatabase(self.db_path)
        self.start_time = datetime.now()
        
    def track_document_access(self, document_path: str, access_type: str, 
                            user_agent: str = "MCP-System", duration_ms: int = None):
        """跟踪文档访问"""
        event = AccessEvent(
            timestamp=datetime.now().isoformat(),
            document_path=document_path,
            access_type=access_type,
            user_agent=user_agent,
            duration_ms=duration_ms
        )
        self.metrics_db.record_access(event)
        logger.debug(f"Tracked document access: {document_path} ({access_type})")
    
    def track_ai_query(self, query_type: str, project_path: str, language: str, 
                      duration_ms: int, tokens_processed: int = None, success: bool = True):
        """跟踪AI查询"""
        event = AIQueryEvent(
            timestamp=datetime.now().isoformat(),
            query_type=query_type,
            project_path=project_path,
            language=language,
            duration_ms=duration_ms,
            tokens_processed=tokens_processed,
            success=success
        )
        self.metrics_db.record_ai_query(event)
        logger.debug(f"Tracked AI query: {query_type} for {project_path}")
    
    def track_document_update(self, update_type: str, files_changed: int, 
                            trigger: str, duration_ms: int = None, success: bool = True):
        """跟踪文档更新"""
        event = UpdateEvent(
            timestamp=datetime.now().isoformat(),
            update_type=update_type,
            files_changed=files_changed,
            trigger=trigger,
            success=success,
            duration_ms=duration_ms
        )
        self.metrics_db.record_update(event)
        logger.info(f"Tracked document update: {update_type} ({files_changed} files)")
    
    def analyze_performance(self, days: int = 7) -> Dict[str, Any]:
        """分析性能数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        stats = self.metrics_db.get_stats(
            start_date.isoformat(), 
            end_date.isoformat()
        )
        
        # 计算性能指标
        analysis = {
            "period": f"{days} days",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "summary": {},
            "recommendations": []
        }
        
        # 文档访问分析
        doc_access = stats.get("document_access", {})
        total_requests = doc_access.get("total_requests", 0)
        avg_duration = doc_access.get("avg_duration_ms", 0)
        
        analysis["summary"]["document_access"] = {
            "total_requests": total_requests,
            "requests_per_day": total_requests / days,
            "avg_response_time_ms": avg_duration
        }
        
        if avg_duration > 1000:  # 超过1秒
            analysis["recommendations"].append("Document access response time is slow (>1s). Consider optimizing file I/O.")
        
        # AI查询分析
        ai_queries = stats.get("ai_queries", {})
        total_queries = ai_queries.get("total_queries", 0)
        
        analysis["summary"]["ai_queries"] = {
            "total_queries": total_queries,
            "queries_per_day": total_queries / days
        }
        
        by_type = ai_queries.get("by_type", {})
        slowest_query_type = max(by_type.keys(), 
                               key=lambda x: by_type[x].get("avg_duration_ms", 0),
                               default=None)
        
        if slowest_query_type:
            slowest_duration = by_type[slowest_query_type]["avg_duration_ms"]
            analysis["summary"]["slowest_query_type"] = {
                "type": slowest_query_type,
                "avg_duration_ms": slowest_duration
            }
            
            if slowest_duration > 5000:  # 超过5秒
                analysis["recommendations"].append(f"AI query type '{slowest_query_type}' is slow (>{slowest_duration:.0f}ms). Consider optimization.")
        
        # 文档更新分析
        doc_updates = stats.get("document_updates", {})
        total_updates = doc_updates.get("total_updates", 0)
        
        analysis["summary"]["document_updates"] = {
            "total_updates": total_updates,
            "updates_per_day": total_updates / days
        }
        
        # 生成健康评分
        health_score = self._calculate_health_score(stats, days)
        analysis["health_score"] = health_score
        
        return analysis
    
    def _calculate_health_score(self, stats: Dict[str, Any], days: int) -> Dict[str, Any]:
        """计算系统健康评分"""
        score = 100
        factors = []
        
        # 文档访问成功率
        doc_access = stats.get("document_access", {})
        by_type = doc_access.get("by_type", {})
        if by_type:
            avg_success_rate = sum(t.get("success_rate", 1) for t in by_type.values()) / len(by_type)
            if avg_success_rate < 0.95:
                penalty = (0.95 - avg_success_rate) * 30
                score -= penalty
                factors.append(f"Document access success rate: {avg_success_rate:.1%} (-{penalty:.1f})")
        
        # AI查询成功率
        ai_queries = stats.get("ai_queries", {})
        ai_by_type = ai_queries.get("by_type", {})
        if ai_by_type:
            avg_ai_success_rate = sum(t.get("success_rate", 1) for t in ai_by_type.values()) / len(ai_by_type)
            if avg_ai_success_rate < 0.90:
                penalty = (0.90 - avg_ai_success_rate) * 40
                score -= penalty
                factors.append(f"AI query success rate: {avg_ai_success_rate:.1%} (-{penalty:.1f})")
        
        # 响应时间
        avg_duration = doc_access.get("avg_duration_ms", 0)
        if avg_duration > 500:
            penalty = min((avg_duration - 500) / 100, 20)
            score -= penalty
            factors.append(f"Slow response time: {avg_duration:.0f}ms (-{penalty:.1f})")
        
        # 更新频率（过于频繁可能表示问题）
        doc_updates = stats.get("document_updates", {})
        updates_per_day = doc_updates.get("total_updates", 0) / days
        if updates_per_day > 20:  # 每天超过20次更新可能异常
            penalty = min((updates_per_day - 20) * 2, 15)
            score -= penalty
            factors.append(f"High update frequency: {updates_per_day:.1f}/day (-{penalty:.1f})")
        
        score = max(0, min(100, score))
        
        # 评级
        if score >= 90:
            grade = "A"
            status = "Excellent"
        elif score >= 80:
            grade = "B" 
            status = "Good"
        elif score >= 70:
            grade = "C"
            status = "Fair"
        elif score >= 60:
            grade = "D"
            status = "Poor"
        else:
            grade = "F"
            status = "Critical"
        
        return {
            "score": round(score, 1),
            "grade": grade,
            "status": status,
            "factors": factors
        }
    
    def generate_report(self, days: int = 7, output_file: str = None) -> Dict[str, Any]:
        """生成性能报告"""
        analysis = self.analyze_performance(days)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "mcp_root": str(self.mcp_root),
            "analysis_period": f"{days} days",
            **analysis
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Performance report saved to: {output_file}")
        
        return report
    
    def cleanup_old_metrics(self, days_to_keep: int = 30):
        """清理旧的指标数据"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 清理各表中的旧数据
            tables = ["document_access", "ai_queries", "document_updates"]
            total_deleted = 0
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE timestamp < ?", (cutoff_date,))
                count_before = cursor.fetchone()[0]
                
                cursor.execute(f"DELETE FROM {table} WHERE timestamp < ?", (cutoff_date,))
                deleted = cursor.rowcount
                total_deleted += deleted
                
                logger.info(f"Cleaned {deleted} old records from {table}")
            
            conn.commit()
            
            # 压缩数据库
            cursor.execute("VACUUM")
            
            logger.info(f"Cleanup completed: removed {total_deleted} old records")

def main():
    parser = argparse.ArgumentParser(description="MCP Performance Monitor")
    parser.add_argument("--mcp-root", default=".", help="MCP root directory")
    parser.add_argument("--db-path", help="Database file path")
    parser.add_argument("--action", choices=["analyze", "report", "cleanup"], 
                       default="analyze", help="Action to perform")
    parser.add_argument("--days", type=int, default=7, help="Number of days to analyze")
    parser.add_argument("--output", help="Output file for reports")
    parser.add_argument("--cleanup-days", type=int, default=30, 
                       help="Days of data to keep during cleanup")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # 创建性能监控器
    monitor = PerformanceMonitor(args.mcp_root, args.db_path)
    
    if args.action == "analyze":
        analysis = monitor.analyze_performance(args.days)
        
        print(f"=== MCP性能分析报告 ({args.days}天) ===")
        print(f"分析期间: {analysis['start_date'][:10]} 到 {analysis['end_date'][:10]}")
        
        # 健康评分
        health = analysis["health_score"]
        print(f"\n🏥 系统健康评分: {health['score']}/100 ({health['grade']} - {health['status']})")
        
        if health["factors"]:
            print("影响因素:")
            for factor in health["factors"]:
                print(f"  • {factor}")
        
        # 摘要统计
        summary = analysis["summary"]
        
        if "document_access" in summary:
            doc_stats = summary["document_access"]
            print(f"\n📄 文档访问:")
            print(f"  • 总请求数: {doc_stats['total_requests']}")
            print(f"  • 日均请求: {doc_stats['requests_per_day']:.1f}")
            print(f"  • 平均响应时间: {doc_stats['avg_response_time_ms']:.0f}ms")
        
        if "ai_queries" in summary:
            ai_stats = summary["ai_queries"]
            print(f"\n🤖 AI查询:")
            print(f"  • 总查询数: {ai_stats['total_queries']}")
            print(f"  • 日均查询: {ai_stats['queries_per_day']:.1f}")
            
            if "slowest_query_type" in summary:
                slowest = summary["slowest_query_type"]
                print(f"  • 最慢查询类型: {slowest['type']} ({slowest['avg_duration_ms']:.0f}ms)")
        
        if "document_updates" in summary:
            update_stats = summary["document_updates"]
            print(f"\n📝 文档更新:")
            print(f"  • 总更新次数: {update_stats['total_updates']}")
            print(f"  • 日均更新: {update_stats['updates_per_day']:.1f}")
        
        # 建议
        if analysis["recommendations"]:
            print(f"\n💡 优化建议:")
            for rec in analysis["recommendations"]:
                print(f"  • {rec}")
        
        if not analysis["recommendations"]:
            print(f"\n✅ 系统运行良好，无需优化")
    
    elif args.action == "report":
        output_file = args.output or f"performance-report-{datetime.now().strftime('%Y%m%d')}.json"
        report = monitor.generate_report(args.days, output_file)
        print(f"✅ Performance report generated: {output_file}")
        print(f"📊 Health Score: {report['health_score']['score']}/100")
    
    elif args.action == "cleanup":
        monitor.cleanup_old_metrics(args.cleanup_days)
        print(f"✅ Cleaned up metrics older than {args.cleanup_days} days")
    
    return 0

if __name__ == "__main__":
    exit(main())

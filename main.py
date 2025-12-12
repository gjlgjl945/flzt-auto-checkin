import os
import requests
import json
from dotenv import load_dotenv
import sys
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0'
}


def load_env():
    """加载环境变量"""
    print("=" * 50)
    print("开始加载环境变量...")
    load_dotenv()
    env = os.environ
    
    # 检查必要环境变量
    required_vars = ['BASE_URL', 'EMAIL', 'PASSWORD']
    missing_vars = [var for var in required_vars if var not in env or not env[var]]
    
    if missing_vars:
        print(f"❌ 缺少必要环境变量: {missing_vars}")
        print("请确保 .env 文件中包含以下变量:")
        for var in missing_vars:
            print(f"  - {var}")
        sys.exit(1)
    
    print("✅ 环境变量加载成功")
    print(f"BASE_URL: {env.get('BASE_URL', '未设置')}")
    print(f"EMAIL: {env.get('EMAIL', '未设置')}")
    print(f"PASSWORD: {'*' * len(env.get('PASSWORD', ''))} (长度: {len(env.get('PASSWORD', ''))})")
    return dict(env)


def login(url, email, password):
    """用户登录"""
    print("\n" + "=" * 50)
    print(f"开始登录...")
    print(f"登录URL: {url}")
    print(f"登录邮箱: {email}")
    
    # 根据浏览器请求，使用表单格式发送数据
    form_data = {
        'email': email,
        'password': password
    }
    
    # 使用表单格式的请求头
    request_headers = headers.copy()
    request_headers['Content-Type'] = 'application/x-www-form-urlencoded'
    request_headers['Origin'] = 'https://fljc.cc'
    request_headers['Referer'] = 'https://fljc.cc/auth/login'
    
    try:
        # 使用data参数发送表单数据
        response = requests.post(url=url, data=form_data, headers=request_headers, timeout=30)
        print(f"登录响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 登录失败 - 状态码异常: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
        
        try:
            data = json.loads(response.text)
            print(f"登录响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 根据提供的响应格式，优先获取 auth_data
            if 'data' in data and 'auth_data' in data['data']:
                auth_data = data['data']['auth_data']
                print(f"✅ 登录成功")
                print(f"获取到Auth Data: {auth_data}")
                return auth_data
            else:
                print(f"❌ 登录失败 - 响应中未找到auth_data")
                print(f"响应结构: {data}")
                return None
                
        except json.JSONDecodeError as e:
            print(f"❌ 登录失败 - JSON解析错误: {e}")
            print(f"原始响应: {response.text[:500]}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ 登录失败 - 请求超时")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ 登录失败 - 连接错误")
        return None
    except Exception as e:
        print(f"❌ 登录失败 - 未知错误: {e}")
        return None


def try_checkin(url, auth_data, method='POST'):
    """尝试不同的签到接口"""
    headers_copy = headers.copy()
    headers_copy['Authorization'] = auth_data
    headers_copy['Referer'] = 'https://fljc.cc/user'
    
    try:
        if method == 'POST':
            response = requests.post(url=url, headers=headers_copy, timeout=30)
        else:
            response = requests.get(url=url, headers=headers_copy, timeout=30)
        
        print(f"尝试签到 - 方法: {method}, 状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = json.loads(response.text)
                print(f"签到响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return True, data
            except json.JSONDecodeError:
                # 可能返回的不是JSON
                print(f"响应内容: {response.text[:200]}")
                return False, None
        elif response.status_code == 404:
            print(f"接口不存在: {url}")
            return False, None
        else:
            print(f"意外状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"请求异常: {e}")
        return False, None


def checkin(base_url, auth_data):
    """执行签到 - 尝试多个可能的接口"""
    print("\n" + "=" * 50)
    print("开始签到...")
    
    # 获取当前时间戳（毫秒）
    current_timestamp = int(time.time() * 1000)
    
    # 尝试多个可能的签到接口
    possible_checkin_endpoints = [
        f"{base_url}/api/v1/user/checkin?t={current_timestamp}",  # 原始尝试
        f"{base_url}/api/v1/user/checkin",  # 不带时间戳
        f"{base_url}/api/v1/passport/comm/checkin",  # 其他可能的路径
        f"{base_url}/user/checkin",  # 简化路径
        f"{base_url}/checkin",  # 更简化路径
    ]
    
    # 同时尝试GET和POST方法
    for endpoint in possible_checkin_endpoints:
        print(f"\n尝试签到接口: {endpoint}")
        
        # 先尝试POST
        success, data = try_checkin(endpoint, auth_data, method='POST')
        if success:
            print(f"✅ 找到签到接口: {endpoint} (POST)")
            return True, data
        
        # 再尝试GET
        success, data = try_checkin(endpoint, auth_data, method='GET')
        if success:
            print(f"✅ 找到签到接口: {endpoint} (GET)")
            return True, data
    
    print("\n❌ 所有可能的签到接口都失败")
    return False, None


def get_user_info(url, auth_data):
    """获取用户信息"""
    print("\n" + "=" * 50)
    print("获取用户信息...")
    print(f"用户信息URL: {url}")
    
    headers_copy = headers.copy()
    headers_copy['Authorization'] = auth_data
    headers_copy['Referer'] = 'https://fljc.cc/dashboard'
    
    try:
        response = requests.get(url=url, headers=headers_copy, timeout=30)
        print(f"用户信息响应状态码: {response.status_code}")
        
        try:
            data = json.loads(response.text)
            print(f"用户信息响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if 'status' in data and data['status'] == 'success' and 'data' in data:
                user_data = data['data']
                print("✅ 用户信息获取成功")
                
                # 打印关键用户信息
                if 'email' in user_data:
                    print(f"用户邮箱: {user_data.get('email')}")
                if 'plan' in user_data:
                    print(f"当前套餐: {user_data.get('plan')}")
                if 'plan_time' in user_data:
                    print(f"套餐到期时间: {user_data.get('plan_time')}")
                if 'balance' in user_data:
                    print(f"账户余额: {user_data.get('balance')}")
                if 'transfer_enable' in user_data:
                    total = int(user_data.get('transfer_enable', 0))
                    used = int(user_data.get('used', 0)) if 'used' in user_data else 0
                    remaining = total - used
                    print(f"总流量: {total / 1024 / 1024 / 1024:.2f} GB")
                    print(f"已用流量: {used / 1024 / 1024 / 1024:.2f} GB")
                    print(f"剩余流量: {remaining / 1024 / 1024 / 1024:.2f} GB")
                
                # 检查可能的签到流量字段
                checkin_fields = ['transfer_checkin', 'checkin_reward_traffic', 'checkin_traffic', 'reward_traffic']
                for field in checkin_fields:
                    if field in user_data:
                        checkin_traffic = int(user_data.get(field, 0))
                        print(f"签到流量 ({field}): {checkin_traffic / 1024 / 1024:.2f} MB")
                        user_data['checkin_traffic'] = checkin_traffic
                
                return user_data
            else:
                print("❌ 用户信息获取失败 - 响应格式异常")
                return None
                
        except json.JSONDecodeError as e:
            print(f"❌ 用户信息响应解析失败: {e}")
            print(f"原始响应: {response.text[:500]}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ 获取用户信息失败 - 请求超时")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ 获取用户信息失败 - 连接错误")
        return None
    except Exception as e:
        print(f"❌ 获取用户信息失败 - 未知错误: {e}")
        return None


def convert_traffic(base_url, auth_data, traffic):
    """转换流量"""
    print("\n" + "=" * 50)
    print("开始流量转换...")
    print(f"转换流量: {traffic} MB")
    
    # 获取当前时间戳（毫秒）
    current_timestamp = int(time.time() * 1000)
    
    # 尝试多个可能的流量转换接口
    possible_convert_endpoints = [
        f"{base_url}/api/v1/user/koukanntraffic?t={current_timestamp}",
        f"{base_url}/api/v1/user/koukanntraffic",
        f"{base_url}/api/v1/user/convert/traffic",
        f"{base_url}/api/v1/user/traffic/convert",
        f"{base_url}/user/convert",
    ]
    
    headers_copy = headers.copy()
    headers_copy['Authorization'] = auth_data
    headers_copy['Referer'] = 'https://fljc.cc/user'
    
    for endpoint in possible_convert_endpoints:
        print(f"\n尝试流量转换接口: {endpoint}")
        
        # 对于流量转换，使用GET请求并传递参数
        params = {
            'traffic': str(traffic)
        }
        
        try:
            response = requests.get(url=endpoint, headers=headers_copy, params=params, timeout=30)
            print(f"流量转换响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = json.loads(response.text)
                    print(f"流量转换响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    if 'status' in data:
                        if data['status'] == 'success':
                            print(f"✅ 流量转换成功!")
                            return True
                        else:
                            print(f"❌ 流量转换失败")
                    elif 'msg' in data:
                        print(f"✅ 流量转换结果: {data['msg']}")
                        return True
                    elif 'message' in data:
                        print(f"✅ 流量转换消息: {data['message']}")
                        return True
                    else:
                        print(f"⚠️ 流量转换响应中未找到状态字段")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ 流量转换响应解析失败: {e}")
                    print(f"原始响应: {response.text[:500]}")
            elif response.status_code == 404:
                print(f"接口不存在: {endpoint}")
            else:
                print(f"意外状态码: {response.status_code}")
                print(f"响应内容: {response.text[:200]}")
                
        except Exception as e:
            print(f"请求异常: {e}")
    
    print("\n❌ 所有可能的流量转换接口都失败")
    return False


def main():
    """主函数"""
    print("🚀 开始执行签到脚本")
    print("=" * 50)
    
    # 加载环境变量
    env = load_env()
    
    # 构建URL
    base_url = env['BASE_URL'].rstrip('/')
    
    # 获取当前时间戳（毫秒）
    current_timestamp = int(time.time() * 1000)
    
    login_url = f"{base_url}/api/v1/passport/auth/login?t={current_timestamp}"
    user_info_url = f"{base_url}/api/v1/user/info?t={current_timestamp}"
    
    email = env['EMAIL']
    password = env['PASSWORD']
    
    # 登录
    auth_data = login(url=login_url, email=email, password=password)
    if auth_data is None:
        print("\n❌ 登录失败，脚本终止")
        return
    
    # 获取用户信息
    user_data = get_user_info(url=user_info_url, auth_data=auth_data)
    if user_data is None:
        print("\n⚠️ 获取用户信息失败，跳过后续操作")
        return
    
    # 尝试签到
    checkin_success, checkin_response = checkin(base_url, auth_data)
    
    if checkin_success:
        print(f"✅ 签到成功!")
        
        # 解析签到响应
        if checkin_response:
            if 'data' in checkin_response and 'checkin_reward_traffic' in checkin_response['data']:
                traffic_bytes = int(checkin_response['data']['checkin_reward_traffic'])
                traffic_mb = int(traffic_bytes / 1024 / 1024)
                print(f"📊 签到获得流量: {traffic_bytes} 字节 = {traffic_mb} MB")
                
                if traffic_mb > 0:
                    # 等待几秒让系统处理
                    print("等待系统处理签到数据...")
                    time.sleep(3)
                    
                    # 尝试转换流量
                    convert_success = convert_traffic(base_url, auth_data, traffic_mb)
                    if not convert_success:
                        print("⚠️ 流量转换失败，但签到已完成")
            else:
                print("⚠️ 签到响应中没有找到流量奖励信息")
    else:
        print("⚠️ 签到失败，可能今天已经签到过了，或者签到接口有变化")
    
    # 重新获取用户信息查看最新状态
    print("\n" + "=" * 50)
    print("获取最新用户信息...")
    user_data = get_user_info(url=user_info_url, auth_data=auth_data)
    
    print("\n" + "=" * 50)
    print("✅ 脚本执行完成")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断执行")
    except Exception as e:
        print(f"\n\n❌ 脚本执行出错: {e}")
        import traceback
        traceback.print_exc()

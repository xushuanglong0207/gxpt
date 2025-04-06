declare module '*.css';
declare module '*.less';
declare module '*.scss';
declare module '*.svg';
declare module '*.png';
declare module '*.jpg';
declare module '*.jpeg';
declare module '*.gif';
declare module '*.bmp';
declare module '*.tiff';

interface Window {
  __REDUX_DEVTOOLS_EXTENSION_COMPOSE__: any;
}

declare module 'react' {
  interface HTMLProps {
    type?: any;
  }
}

declare module '@/types/testCase' {
  export interface TestCase {
    id: string;
    title: string;
    steps: string;
    expectedResults: string;
    status: 'draft' | 'active' | 'completed' | 'archived';
    priority: 'low' | 'medium' | 'high' | 'critical';
    createdAt: string;
    updatedAt: string;
    category?: string;
  }
}

declare module 'react-quill' {
  import * as React from 'react';
  
  interface ReactQuillProps {
    value?: string;
    onChange?: (content: string) => void;
    theme?: string;
    modules?: any;
    formats?: string[];
    bounds?: string | HTMLElement;
    placeholder?: string;
    preserveWhitespace?: boolean;
    readOnly?: boolean;
    scrollingContainer?: string | HTMLElement;
    style?: React.CSSProperties;
  }
  
  class ReactQuill extends React.Component<ReactQuillProps> {}
  export default ReactQuill;
}

declare module 'echarts-for-react' {
  import * as React from 'react';
  
  interface EChartsReactProps {
    option: any;
    notMerge?: boolean;
    lazyUpdate?: boolean;
    style?: React.CSSProperties;
    className?: string;
    theme?: string | object;
    onEvents?: Record<string, Function>;
    opts?: {
      devicePixelRatio?: number;
      renderer?: 'canvas' | 'svg';
      width?: number | string;
      height?: number | null;
    };
  }
  
  class ReactEcharts extends React.Component<EChartsReactProps> {
    getEchartsInstance: () => any;
  }
  
  export default ReactEcharts;
}

declare module '@ant-design/icons' {
  import * as React from 'react';
  
  interface IconProps {
    className?: string;
    style?: React.CSSProperties;
    spin?: boolean;
    rotate?: number;
    twoToneColor?: string;
  }
  
  type IconComponent = React.FC<IconProps>;
  
  // 基础图标
  export const FileTextOutlined: IconComponent;
  export const UserOutlined: IconComponent;
  export const FieldTimeOutlined: IconComponent;
  export const EyeOutlined: IconComponent;
  export const LikeOutlined: IconComponent;
  export const MessageOutlined: IconComponent;
  export const ShareAltOutlined: IconComponent;
  export const SearchOutlined: IconComponent;
  export const PlusOutlined: IconComponent;
  export const EditOutlined: IconComponent;
  export const DeleteOutlined: IconComponent;
  export const BookOutlined: IconComponent;
  export const CalendarOutlined: IconComponent;
  export const FilterOutlined: IconComponent;
  export const UploadOutlined: IconComponent;
  export const DownloadOutlined: IconComponent;
  export const ExclamationCircleOutlined: IconComponent;
  
  // 导航图标
  export const HomeOutlined: IconComponent;
  export const DashboardOutlined: IconComponent;
  export const MenuFoldOutlined: IconComponent;
  export const MenuUnfoldOutlined: IconComponent;
  export const GlobalOutlined: IconComponent;
  export const AppstoreOutlined: IconComponent;
  export const SettingOutlined: IconComponent;
  export const TeamOutlined: IconComponent;
  export const FolderOutlined: IconComponent;
  export const FolderOpenOutlined: IconComponent;
  export const BarsOutlined: IconComponent;
  
  // 操作图标
  export const CheckOutlined: IconComponent;
  export const CloseOutlined: IconComponent;
  export const PlusCircleOutlined: IconComponent;
  export const MinusCircleOutlined: IconComponent;
  export const InfoCircleOutlined: IconComponent;
  export const QuestionCircleOutlined: IconComponent;
  export const CheckCircleOutlined: IconComponent;
  export const CloseCircleOutlined: IconComponent;
  export const WarningOutlined: IconComponent;
  export const StopOutlined: IconComponent;
  export const SyncOutlined: IconComponent;
  export const ReloadOutlined: IconComponent;
  export const LoadingOutlined: IconComponent;
  
  // 品牌和标志
  export const GithubOutlined: IconComponent;
  export const TwitterOutlined: IconComponent;
  export const FacebookOutlined: IconComponent;
  export const GoogleOutlined: IconComponent;
  export const LinkedinOutlined: IconComponent;
  export const YoutubeOutlined: IconComponent;
  export const InstagramOutlined: IconComponent;
  export const WechatOutlined: IconComponent;
  export const AlipayOutlined: IconComponent;
  export const TaobaoOutlined: IconComponent;
  export const WeiboOutlined: IconComponent;
  
  // 通用图标
  export const FileOutlined: IconComponent;
  export const BellOutlined: IconComponent;
  export const MailOutlined: IconComponent;
  export const StarOutlined: IconComponent;
  export const HeartOutlined: IconComponent;
  export const EnvironmentOutlined: IconComponent;
  export const PhoneOutlined: IconComponent;
  export const ClockCircleOutlined: IconComponent;
  export const TagOutlined: IconComponent;
  export const TagsOutlined: IconComponent;
  export const KeyOutlined: IconComponent;
  export const FlagOutlined: IconComponent;
  export const LockOutlined: IconComponent;
  export const UnlockOutlined: IconComponent;
  export const HistoryOutlined: IconComponent;
  export const LogoutOutlined: IconComponent;
  export const LoginOutlined: IconComponent;
  export const CopyOutlined: IconComponent;
  export const ShareAltOutlined: IconComponent;
  export const PrinterOutlined: IconComponent;
  export const ExportOutlined: IconComponent;
  export const ImportOutlined: IconComponent;
  export const FormatPainterOutlined: IconComponent;
  export const EllipsisOutlined: IconComponent;
  export const MoreOutlined: IconComponent;
  export const AreaChartOutlined: IconComponent;
  export const PieChartOutlined: IconComponent;
  export const BarChartOutlined: IconComponent;
  export const LineChartOutlined: IconComponent;
  export const RadarChartOutlined: IconComponent;
  export const HeatMapOutlined: IconComponent;
  export const FundOutlined: IconComponent;
  export const ThunderboltOutlined: IconComponent;
  export const RocketOutlined: IconComponent;
  export const DatabaseOutlined: IconComponent;
  export const CloudOutlined: IconComponent;
  export const CloudUploadOutlined: IconComponent;
  export const CloudDownloadOutlined: IconComponent;
  export const CloudServerOutlined: IconComponent;
  export const ApartmentOutlined: IconComponent;
  export const PlayCircleOutlined: IconComponent;
  export const BookFilled: IconComponent;
  export const FileExcelOutlined: IconComponent;
  export const FileAddOutlined: IconComponent;
  export const FileSearchOutlined: IconComponent;
  export const SortAscendingOutlined: IconComponent;
  export const SortDescendingOutlined: IconComponent;
  export const LinkOutlined: IconComponent;
  export const ApiOutlined: IconComponent;
  export const RobotOutlined: IconComponent;
  export const ToolOutlined: IconComponent;
  export const LaptopOutlined: IconComponent;
  
  // 文本编辑图标
  export const BoldOutlined: IconComponent;
  export const ItalicOutlined: IconComponent;
  export const UnderlineOutlined: IconComponent;
  export const StrikethroughOutlined: IconComponent;
  export const OrderedListOutlined: IconComponent;
  export const UnorderedListOutlined: IconComponent;
  export const AlignLeftOutlined: IconComponent;
  export const AlignCenterOutlined: IconComponent;
  export const AlignRightOutlined: IconComponent;
}

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
} 
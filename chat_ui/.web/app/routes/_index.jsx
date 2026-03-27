import {Fragment,useCallback,useContext,useEffect} from "react"
import {Box as RadixThemesBox,Button as RadixThemesButton,Code as RadixThemesCode,Container as RadixThemesContainer,Flex as RadixThemesFlex,Heading as RadixThemesHeading,IconButton as RadixThemesIconButton,Link as RadixThemesLink,ScrollArea as RadixThemesScrollArea,Spinner as RadixThemesSpinner,Text as RadixThemesText,TextArea as RadixThemesTextArea} from "@radix-ui/themes"
import {ColorModeContext,EventLoopContext,StateContexts} from "$/utils/context"
import {ReflexEvent,isTrue} from "$/utils/state"
import {Moon as LucideMoon,Send as LucideSend,Sun as LucideSun} from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import remarkGfm from "remark-gfm"
import rehypeKatex from "rehype-katex"
import "katex/dist/katex.min.css"
import rehypeRaw from "rehype-raw"
import rehypeUnwrapImages from "rehype-unwrap-images"
import {Link as ReactRouterLink} from "react-router"
import {PrismAsyncLight as SyntaxHighlighter} from "react-syntax-highlighter"
import oneLight from "react-syntax-highlighter/dist/esm/styles/prism/one-light"
import oneDark from "react-syntax-highlighter/dist/esm/styles/prism/one-dark"
import DebounceInput from "react-debounce-input"
import {jsx} from "@emotion/react"




function Fragment_4eccfd74653df2c248da64de2d1cc715 () {
  const { resolvedColorMode } = useContext(ColorModeContext)



  return (
    jsx(Fragment,{},((resolvedColorMode?.valueOf?.() === "light"?.valueOf?.())?(jsx(Fragment,{},jsx(LucideSun,{},))):(jsx(Fragment,{},jsx(LucideMoon,{},)))))
  )
}


function Iconbutton_3bedd826d25a324edade2a6a1f71ed90 () {
  const { toggleColorMode } = useContext(ColorModeContext)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_9922dd3e837b9e087c86a2522c2c93f8 = useCallback(toggleColorMode, [addEvents, ReflexEvent, toggleColorMode])

  return (
    jsx(RadixThemesIconButton,{css:({ ["padding"] : "6px", ["position"] : "fixed", ["top"] : "2rem", ["right"] : "2rem", ["background"] : "transparent", ["color"] : "inherit", ["zIndex"] : "20", ["&:hover"] : ({ ["cursor"] : "pointer" }) }),onClick:on_click_9922dd3e837b9e087c86a2522c2c93f8},jsx(Fragment_4eccfd74653df2c248da64de2d1cc715,{},))
  )
}


        function ComponentMap_d59534cfa3df3086665270d8af3d1699 () {
            const { resolvedColorMode } = useContext(ColorModeContext)



            return (
                ({ ["h1"] : (({node, children, ...props}) => (jsx(RadixThemesHeading,{as:"h1",css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),size:"6",...props},children))), ["h2"] : (({node, children, ...props}) => (jsx(RadixThemesHeading,{as:"h2",css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),size:"5",...props},children))), ["h3"] : (({node, children, ...props}) => (jsx(RadixThemesHeading,{as:"h3",css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),size:"4",...props},children))), ["h4"] : (({node, children, ...props}) => (jsx(RadixThemesHeading,{as:"h4",css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),size:"3",...props},children))), ["h5"] : (({node, children, ...props}) => (jsx(RadixThemesHeading,{as:"h5",css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),size:"2",...props},children))), ["h6"] : (({node, children, ...props}) => (jsx(RadixThemesHeading,{as:"h6",css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),size:"1",...props},children))), ["p"] : (({node, children, ...props}) => (jsx(RadixThemesText,{as:"p",css:({ ["marginTop"] : "1em", ["marginBottom"] : "1em" }),...props},children))), ["ul"] : (({node, children, ...props}) => (jsx("ul",{css:({ ["listStyleType"] : "disc", ["marginTop"] : "1em", ["marginBottom"] : "1em", ["marginLeft"] : "1.5rem", ["direction"] : "column" }),...props},children))), ["ol"] : (({node, children, ...props}) => (jsx("ol",{css:({ ["listStyleType"] : "decimal", ["marginTop"] : "1em", ["marginBottom"] : "1em", ["marginLeft"] : "1.5rem", ["direction"] : "column" }),...props},children))), ["li"] : (({node, children, ...props}) => (jsx("li",{css:({ ["marginTop"] : "0.5em", ["marginBottom"] : "0.5em" }),...props},children))), ["a"] : (({node, children, ...props}) => (jsx(RadixThemesLink,{css:({ ["&:hover"] : ({ ["color"] : "var(--accent-8)" }) }),href:"#",...props},children))), ["code"] : (({node, children, ...props}) => (jsx(RadixThemesCode,{...props},children))), ["pre"] : (({node, ...rest}) => { const {node: childNode, className, children: components, ...props} = rest.children.props; const children = String(Array.isArray(components) ? components.join('\n') : components).replace(/\n$/, ''); const match = (className || '').match(/language-(?<lang>.*)/); let _language = match ? match[1] : ''; ;             return jsx(SyntaxHighlighter,{children:children,css:({ ["marginTop"] : "1em", ["marginBottom"] : "1em" }),language:_language,style:((resolvedColorMode?.valueOf?.() === "light"?.valueOf?.()) ? oneLight : oneDark),wrapLongLines:true,...props},);         }) })
            )
        }
        

function Flex_1d1a6fa407a879acbc11fcb2d4478796 () {
  const reflex___state____state__chat_ui___chat_ui____state = useContext(StateContexts.reflex___state____state__chat_ui___chat_ui____state)



  return (
    jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["padding"] : "2em" }),direction:"column",gap:"2"},Array.prototype.map.call(reflex___state____state__chat_ui___chat_ui____state.messages_rx_state_ ?? [],((msg_rx_state_,index_aaf77ca8e33f39d93c99a5fd3ec245d6)=>(jsx(RadixThemesFlex,{css:({ ["width"] : "100%", ["marginBottom"] : "1em" }),justify:((msg_rx_state_?.["role"]?.valueOf?.() === "user"?.valueOf?.()) ? "end" : "start"),key:index_aaf77ca8e33f39d93c99a5fd3ec245d6},jsx(RadixThemesBox,{css:({ ["background"] : ((msg_rx_state_?.["role"]?.valueOf?.() === "user"?.valueOf?.()) ? "var(--jade-9)" : "var(--gray-3)"), ["color"] : ((msg_rx_state_?.["role"]?.valueOf?.() === "user"?.valueOf?.()) ? "white" : "black"), ["padding"] : "12px 16px", ["borderRadius"] : "18px", ["maxWidth"] : "75%", ["boxShadow"] : "0 2px 4px rgba(0,0,0,0.1)" })},jsx("div",{},jsx(ReactMarkdown,{components:ComponentMap_d59534cfa3df3086665270d8af3d1699(),rehypePlugins:[rehypeKatex, rehypeRaw, rehypeUnwrapImages],remarkPlugins:[remarkMath, remarkGfm]},msg_rx_state_?.["content"]))))))))
  )
}


function Debounceinput_0bf0797c8f4e68ac1400591613f4efc2 () {
  const reflex___state____state__chat_ui___chat_ui____state = useContext(StateContexts.reflex___state____state__chat_ui___chat_ui____state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_change_1e2b252befcc436aec757df4bf8ae15a = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.chat_ui___chat_ui____state.set_user_input", ({ ["value"] : _e?.["target"]?.["value"] }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(DebounceInput,{css:({ ["width"] : "100%", ["height"] : "80px", ["borderRadius"] : "10px", ["background"] : "white", ["border"] : "1px solid #cbd5e1" }),debounceTimeout:300,element:RadixThemesTextArea,onChange:on_change_1e2b252befcc436aec757df4bf8ae15a,placeholder:"Pergunte algo...",value:reflex___state____state__chat_ui___chat_ui____state.user_input_rx_state_},)
  )
}


function Fragment_a227e3046ef46286fa34611333c1c205 () {
  const reflex___state____state__chat_ui___chat_ui____state = useContext(StateContexts.reflex___state____state__chat_ui___chat_ui____state)



  return (
    jsx(Fragment,{},(reflex___state____state__chat_ui___chat_ui____state.is_working_rx_state_?(jsx(Fragment,{},jsx(RadixThemesSpinner,{size:"2"},))):(jsx(Fragment,{},jsx(LucideSend,{},)))))
  )
}


function Button_6b991ad252a25e41865990d7883044e4 () {
  const reflex___state____state__chat_ui___chat_ui____state = useContext(StateContexts.reflex___state____state__chat_ui___chat_ui____state)
const [addEvents, connectErrors] = useContext(EventLoopContext);

const on_click_ee211c9e3df5b4d512f1d776224b3d40 = useCallback(((_e) => (addEvents([(ReflexEvent("reflex___state____state.chat_ui___chat_ui____state.answer", ({  }), ({  })))], [_e], ({  })))), [addEvents, ReflexEvent])

  return (
    jsx(RadixThemesButton,{color:"jade",css:({ ["padding"] : "1.5em", ["cursor"] : "pointer" }),disabled:reflex___state____state__chat_ui___chat_ui____state.is_working_rx_state_,onClick:on_click_ee211c9e3df5b4d512f1d776224b3d40,radius:"full",size:"4"},jsx(Fragment_a227e3046ef46286fa34611333c1c205,{},))
  )
}


export default function Component() {





  return (
    jsx(Fragment,{},jsx(RadixThemesContainer,{css:({ ["padding"] : "16px", ["maxWidth"] : "800px", ["margin"] : "0 auto", ["paddingTop"] : "5vh" }),size:"3"},jsx(Iconbutton_3bedd826d25a324edade2a6a1f71ed90,{},),jsx(RadixThemesFlex,{align:"center",className:"rx-Stack",css:({ ["width"] : "100%" }),direction:"column",gap:"3"},jsx(RadixThemesHeading,{css:({ ["marginBottom"] : "1em" }),size:"7"},"Ollama Chat (Reflex)"),jsx(RadixThemesText,{as:"p",css:({ ["color"] : "gray" }),size:"2"},"Modelo: qwen3-vl:2b")),jsx(RadixThemesScrollArea,{css:({ ["height"] : "60vh", ["border"] : "1px solid #e2e8f0", ["borderRadius"] : "10px", ["backgroundColor"] : "#f8fafc", ["width"] : "100%" })},jsx(Flex_1d1a6fa407a879acbc11fcb2d4478796,{},)),jsx(RadixThemesFlex,{align:"start",className:"rx-Stack",css:({ ["width"] : "100%", ["paddingTop"] : "1em", ["alignItems"] : "end" }),direction:"row",gap:"3"},jsx(Debounceinput_0bf0797c8f4e68ac1400591613f4efc2,{},),jsx(Button_6b991ad252a25e41865990d7883044e4,{},))),jsx("title",{},"Ollama Chat"),jsx("meta",{content:"favicon.ico",property:"og:image"},))
  )
}